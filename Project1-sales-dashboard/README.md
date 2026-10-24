# Sales Performance Dashboard

**Tools:** Power BI | SQL | Excel

## Project overview
This project analyses retail sales data to show how sales and profit perform across regions, months and products.
The Power BI dashboard gives managers a quick view of total sales, profit and profit margin, and helps them see where the business earns and where it loses margin.

![Sales dashboard](Images/dashboard.png)

## Business questions
1. How much does the business sell, and how much profit does it make?
2. Which regions earn the best and the worst profit margin?
3. How do sales change across the year?
4. Which products bring in the most sales?

## Dashboard (`sales_dashboard (1).pbix`)
- **KPI cards:** total sales, total profit and profit margin
- **Region slicer:** Central, East, South and West
- **Charts:** profit margin by region, total sales by month, and total sales by product

## Key findings

| KPI | Value |
|---|---|
| Total sales | about 2.30M |
| Total profit | about 286K |
| Profit margin | 12.47% |

1. **West has the best profit margin (14.94%)**, followed by East (13.48%) and South (11.93%).
2. **Central has the weakest margin (7.92%)**, far below the 12.47% average. It is the region that most needs a pricing or discount review.
3. **Sales are seasonal.** September to December bring in about half of the year's sales, with the highest months in November (about 0.35M) and December (about 0.33M). February is the lowest month (about 0.06M).
4. **One product leads.** The Canon imageCLASS 2200 Advanced Copier sells about 62K, more than twice the next product in the top 10 (about 27K).

## Recommendations
1. Review discounts and costs in the Central region to lift its margin.
2. Plan stock and marketing around the September to December peak.
3. Run promotions in February and January, the slowest months.
4. Protect availability of the best-selling copier and similar high-value products.

## Project structure
```
Project1-sales-dashboard/
|-- Data/                 source data
|-- Excel/                Excel analysis files
|-- Images/               dashboard screenshot
|-- PowerBi/              Power BI files
|-- Sql/                  SQL queries
|-- sales_dashboard (1).pbix
`-- README.md
```

## How to view
Open `sales_dashboard (1).pbix` in Power BI Desktop. Use the region slicer to see how each region performs.

## Author
**Yash Zade** | yashzade0705@gmail.com | [GitHub](https://github.com/yashzade0705-stack)
