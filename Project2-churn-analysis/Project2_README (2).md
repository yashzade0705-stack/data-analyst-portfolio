# Customer Churn Analysis

**Tools:** Python | SQL | Power BI

## Project overview
Telecom companies lose revenue when customers cancel their service. This project analyses a telecom customer dataset to find **who is leaving, why, and which current customers are at risk**.
It combines exploratory analysis, a churn prediction model and a Power BI dashboard that a retention team could use.

![Churn dashboard](images/dashboard.png)

## Business questions
1. What share of customers churn?
2. Which contract types and customer groups churn the most?
3. How does churn change with how long a customer has stayed?
4. Which factors drive churn the most?
5. Which current customers are at high risk of leaving?

## Dataset
Telecom customer data with about 7,000 customers. It includes contract type, tenure, internet service, payment method, billing, charges, extra services and whether the customer churned.

## Method
- Cleaned and prepared the data in Python and SQL
- Grouped customers by tenure (0-12, 13-24, 25-48 and 49+ months)
- Built a churn prediction pipeline in `churn_model.py` with scikit-learn (one-hot encoding, scaling, Logistic Regression and Random Forest), checked with a train/test split, a classification report and ROC AUC
- Scored each customer and assigned a risk band (High, Medium or Low)
- Saved model metrics, feature importance and customer predictions to the `outputs/` folder
- Loaded `churn_predictions.csv` into Power BI and built the dashboard from it

## Dashboard
- **KPI cards:** customers, churned customers, churn rate, high-risk customers
- **Risk band slicer:** High, Medium, Low
- **Charts:** churn rate by contract, churn rate by tenure group, a contract vs tenure heatmap, and the top factors driving churn

## Key findings

| KPI | Value |
|---|---|
| Customers | 7,032 |
| Churned customers | 1,869 |
| Churn rate | 26.58% |
| High-risk customers | 2,391 |

1. **Contract type is the strongest signal.** Month-to-month customers churn at 42.71%, against 11.28% for one-year and 2.85% for two-year contracts. Month-to-month churn is about 15 times the two-year rate.
2. **New customers leave the most.** Churn is 47.68% in the first 12 months and falls to 28.71% (13-24 months), 20.39% (25-48 months) and 9.51% after 49 months.
3. **The riskiest group is new month-to-month customers.** The heatmap shows 51.35% churn for month-to-month customers in their first 12 months.
4. **Fiber optic internet is the top churn factor in the model**, followed by total charges and paying by electronic check. Streaming TV, streaming movies and multiple lines also push churn up.
5. **About 2,391 customers (about a third) are marked High risk**, which gives the retention team a ready target list.

## Recommendations
1. Offer discounts or perks to move month-to-month customers onto one-year or two-year contracts.
2. Add an onboarding and check-in programme for customers in their first 12 months.
3. Look into the fiber optic service, since its customers churn the most (check price, speed and support quality).
4. Encourage automatic payment methods instead of electronic check.
5. Use the High-risk list for targeted retention calls and offers.

## Project structure
```
Project2-churn-analysis/
|-- data/            source and cleaned data
|-- images/          dashboard screenshot
|-- outputs/         model metrics, feature importance, churn predictions
|-- PowerBi/         Power BI files
|-- churn_model.py   churn prediction model
`-- README.md
```

## How to run
1. Install the libraries: `pip install pandas scikit-learn matplotlib`
2. Put the Telco churn CSV inside the `data` folder
3. Run `python churn_model.py` from the `Project2-churn-analysis` folder. It writes `model_metrics.txt`, `feature_importance.csv`, `feature_importance.png` and `churn_predictions.csv` to `outputs/`
4. Open the Power BI file (`churn_dashboard.pbix`) in Power BI Desktop

## Author
**Yash Zade** | yashzade0705@gmail.com | [GitHub](https://github.com/yashzade0705-stack)
