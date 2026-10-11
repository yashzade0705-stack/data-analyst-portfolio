# Sales Performance Dashboard

An analysis of 9,994 retail orders (2014-2017) to find which regions underperform and which products drive sales, shown in an interactive Power BI dashboard.

![Dashboard](Images/dashboard.png)

## Business Problem

The business wants to know:

1. How are sales and profit changing over time?
2. Which regions and categories perform best, and which underperform?
3. Which products drive sales, and which lose money?

## Dataset

Retail orders data: **9,994 orders** from 2014 to 2017, with order date, region, category, product, sales, profit, quantity and discount.

## Tools

- **SQL / Excel**: data cleaning and exploration
- **Power BI**: interactive dashboard with DAX measures

## Key Findings

- **Total sales: [WRITE TOTAL SALES FROM YOUR DASHBOARD]** and **total profit: [WRITE TOTAL PROFIT]**.
- **Best region:** [REGION NAME] with [SALES / PROFIT].
- **Weakest region:** [REGION NAME] with [SALES / PROFIT].
- **Top category:** [CATEGORY NAME].
- **Top products** by sales: [PRODUCT 1], [PRODUCT 2], [PRODUCT 3].
- **Trend:** [ONE SENTENCE, e.g. sales grew each year / peak in November].

## Dashboard

The Power BI dashboard (`sales_dashboard.pbix`) contains:

- KPI cards: Total Sales, Total Profit, Orders
- Sales and profit trend over time
- Sales by region and by category
- Top products by sales
- Slicers to filter by year and region

## Recommendations

- Focus improvement efforts on the weakest region.
- Promote the top-selling products and categories.
- Review discounts on products that sell well but lose money.

## Project Structure

```
Project1-sales-dashboard/
├── Images/
│   └── dashboard.png
├── sales_dashboard.pbix
└── README.md
```

## How to Use

Open `sales_dashboard.pbix` in Power BI Desktop to explore the dashboard.
