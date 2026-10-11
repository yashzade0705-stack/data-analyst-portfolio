# Customer Churn Analysis

An end-to-end analysis of telecom customer churn: SQL exploration, a Python prediction model, and a Power BI dashboard that shows who leaves and why.

![Dashboard](images/dashboard.png)

## Business Problem

Losing customers is expensive. This project answers three questions:

1. How many customers leave, and which segments leave most?
2. What factors drive churn?
3. Can we predict which customers are at risk, so the business can act early?

## Dataset

Telco customer churn data: **7,032 customers**, with contract type, tenure, monthly and total charges, services, and payment method. The target is `Churn` (Yes/No).

## Tools

- **SQL**: churn rate by contract, tenure, charges and segments
- **Python** (pandas, scikit-learn): data preparation, logistic regression and random forest models
- **Power BI**: interactive dashboard with DAX measures

## Key Findings

- **1,869 of 7,032 customers churned, an overall churn rate of 26.58%.**
- **Contract type matters most.** Month-to-month customers churn at 42.71%, one-year at 11.28%, and two-year at only 2.85%.
- **New customers are the most at risk.** Churn falls steadily with tenure: 47.68% (0-12 months), 28.71% (13-24), 20.39% (25-48) and 9.51% (49+ months).
- **The danger zone is month-to-month customers in their first year**, where churn reaches 51.35%.
- **Top model factors** include Fiber optic internet service, total charges and paying by electronic check.
- **2,391 customers are flagged High Risk** by the model.

## Model Results

| Model | Accuracy |
|---|---|
| Logistic Regression | about 73% |
| Random Forest | about 76% |

Accuracy alone is misleading here, because predicting "stayed" for every customer is already right 73.4% of the time. The model was built to **catch customers who leave**, so the metrics that matter are:

- **Recall: 79%** of churners are identified
- **ROC-AUC: 0.835**

## Dashboard

The Power BI dashboard (`powerbi/churn_dashboard.pbix`) contains:

- KPI cards: Customers, Churned, Churn Rate, High Risk Customers
- A `risk_band` slicer (High / Medium / Low)
- Churn rate by contract and by tenure group
- A heatmap of contract type against tenure group
- A chart of the top factors driving churn

## Recommendations

- Offer incentives to move month-to-month customers onto one- or two-year contracts.
- Focus retention efforts on customers in their first 12 months.
- Review the Fiber optic service and electronic check payment experience, since both are linked to higher churn.
- Use the High Risk list (`data/churn_predictions.csv`) to prioritise outreach.

## Project Structure

```
Project2-churn-analysis/
├── data/
│   ├── telco_churn.csv
│   ├── q1_contract.csv
│   ├── q2_tenure.csv
│   ├── q3_charges.csv
│   ├── q4_segments.csv
│   ├── churn_predictions.csv
│   └── feature_importance.csv
├── images/
│   ├── dashboard.png
│   └── feature_importance.png
├── python/
│   ├── churn_model.py
│   └── model_metrics.txt
├── sql/
│   └── 01_churn_analysis.sql
├── powerbi/
│   └── churn_dashboard.pbix
└── README.md
```

## How to Run

1. Install the libraries: `pip install pandas scikit-learn matplotlib`
2. Run the model from the project folder: `python python/churn_model.py`
3. Open `powerbi/churn_dashboard.pbix` in Power BI Desktop to explore the dashboard.
