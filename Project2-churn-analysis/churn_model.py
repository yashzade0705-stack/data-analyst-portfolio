"""
Project 2 - Customer Churn Analysis: prediction model
Run from the project2-churn-analysis folder:
    pip install pandas scikit-learn matplotlib
    python churn_model.py
Expects: data/telco_churn.csv  (the original Kaggle file)
Writes : outputs/model_metrics.txt, outputs/feature_importance.csv,
         outputs/churn_predictions.csv (load this into Power BI),
         outputs/feature_importance.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Find the Telco CSV automatically anywhere inside the Data folder
_found = sorted(Path("Data").rglob("*.csv"))
if not _found:
    raise SystemExit("No CSV found inside the Data folder. Put the Telco CSV in Data and try again.")
DATA = _found[0]
print("Using file:", DATA)
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

# ---- 1. Load and clean (same cleaning as the SQL step) ----
df = pd.read_csv(DATA)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna(subset=["TotalCharges"]).reset_index(drop=True)   # drops the 11 tenure-0 rows
print("Rows after cleaning:", len(df))                            # expect 7032

y = (df["Churn"] == "Yes").astype(int)
print("Churn rate: %.2f%%" % (y.mean() * 100))                    # expect ~26.58%

X = df.drop(columns=["customerID", "Churn"])
num_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
cat_cols = [c for c in X.columns if c not in num_cols]

pre = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_cols),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---- 2. Models ----
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(
        n_estimators=300, min_samples_leaf=5, class_weight="balanced", random_state=42
    ),
}

report_lines = []
fitted = {}
for name, clf in models.items():
    pipe = Pipeline([("pre", pre), ("clf", clf)]).fit(X_train, y_train)
    pred = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:, 1]
    fitted[name] = pipe
    block = (
        f"=== {name} ===\n"
        f"ROC-AUC: {roc_auc_score(y_test, proba):.3f}\n"
        f"Confusion matrix [[TN FP],[FN TP]]:\n{confusion_matrix(y_test, pred)}\n"
        f"{classification_report(y_test, pred, target_names=['Stayed', 'Churned'])}\n"
    )
    print(block)
    report_lines.append(block)

(OUT / "model_metrics.txt").write_text("\n".join(report_lines))

# ---- 3. Feature importance (logistic regression coefficients) ----
lr = fitted["Logistic Regression"]
names = lr.named_steps["pre"].get_feature_names_out()
coefs = lr.named_steps["clf"].coef_[0]
imp = (
    pd.DataFrame({"feature": names, "coefficient": coefs})
    .assign(abs_coef=lambda d: d.coefficient.abs())
    .sort_values("abs_coef", ascending=False)
    .drop(columns="abs_coef")
)
imp.to_csv(OUT / "feature_importance.csv", index=False)

top = imp.head(12).iloc[::-1]
plt.figure(figsize=(8, 5))
plt.barh(top["feature"], top["coefficient"],
         color=["#c0392b" if v > 0 else "#2e86c1" for v in top["coefficient"]])
plt.title("Top drivers of churn (red = raises risk, blue = lowers risk)")
plt.tight_layout()
plt.savefig(OUT / "feature_importance.png", dpi=150)

# ---- 4. Score every customer for Power BI ----
scored = df[["customerID", "Contract", "tenure", "MonthlyCharges", "Churn"]].copy()
scored["churn_probability"] = lr.predict_proba(X)[:, 1].round(4)
scored["risk_band"] = pd.cut(
    scored["churn_probability"], [-0.01, 0.3, 0.6, 1.0],
    labels=["Low", "Medium", "High"]
)
scored.to_csv(OUT / "churn_predictions.csv", index=False)
print("Saved files to", OUT.resolve())
