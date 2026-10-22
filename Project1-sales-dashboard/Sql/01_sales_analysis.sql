SELECT region,
       YEAR(order_date) AS year,
       MONTH(order_date) AS month,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(sales), 2) AS total_sales,
       ROUND(SUM(profit), 2) AS total_profit,
       ROUND(SUM(profit) / SUM(sales) * 100, 2) AS margin_pct
FROM superstore_db.superstore
GROUP BY region, YEAR(order_date), MONTH(order_date)
ORDER BY region, year, month;

SELECT region, product_name, revenue, profit, product_rank
FROM (
    SELECT region,
           product_name,
           ROUND(SUM(sales), 2) AS revenue,
           ROUND(SUM(profit), 2) AS profit,
           RANK() OVER (PARTITION BY region ORDER BY SUM(sales) DESC) AS product_rank
    FROM superstore_db.superstore
    GROUP BY region, product_name
) ranked
WHERE product_rank <= 10
ORDER BY region, product_rank;

SELECT region,
       ROUND(SUM(sales), 2) AS total_sales,
       ROUND(SUM(profit), 2) AS total_profit,
       ROUND(SUM(profit) / SUM(sales) * 100, 2) AS margin_pct
FROM superstore_db.superstore
GROUP BY region
ORDER BY margin_pct;


