-- PostgreSQL data-quality checks. Record what you find in the README ("Data quality" section).

-- 2.1 Row counts
SELECT 'orders' AS tbl, COUNT(*) FROM orders
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews;

-- 2.2 Order status mix
SELECT order_status, COUNT(*) AS n, ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM orders GROUP BY 1 ORDER BY 2 DESC;

-- 2.3 customer_id is per-order; customer_unique_id is the real person
SELECT COUNT(DISTINCT customer_id) AS customer_ids, COUNT(DISTINCT customer_unique_id) AS unique_customers
FROM customers;

-- 2.4 Orders with NO items (these vanish in an inner join, understating cancellations)
SELECT o.order_status, COUNT(*) AS orders_without_items
FROM orders o LEFT JOIN order_items i ON o.order_id = i.order_id
WHERE i.order_id IS NULL
GROUP BY 1 ORDER BY 2 DESC;

-- 2.5 Delivered orders missing a delivery date, or delivered before purchase
SELECT
  SUM(CASE WHEN order_status = 'delivered' AND order_delivered_customer_date IS NULL THEN 1 ELSE 0 END) AS delivered_no_date,
  SUM(CASE WHEN order_delivered_customer_date < order_purchase_timestamp THEN 1 ELSE 0 END) AS delivered_before_purchase
FROM orders;

-- 2.6 Orders with more than one review
SELECT COUNT(*) AS orders_with_multiple_reviews
FROM (SELECT order_id FROM order_reviews GROUP BY 1 HAVING COUNT(*) > 1) t;

-- 2.7 Duplicate review_ids
SELECT COUNT(*) AS duplicated_review_ids
FROM (SELECT review_id FROM order_reviews GROUP BY 1 HAVING COUNT(*) > 1) t;

-- 2.8 Products with no category
SELECT COUNT(*) AS products_without_category FROM products WHERE product_category_name IS NULL;

-- 2.9 Revenue definitions: items vs items+freight vs payments
SELECT
  ROUND(SUM(price)::numeric, 2)                         AS items_price,
  ROUND(SUM(price + freight_value)::numeric, 2)         AS items_plus_freight,
  (SELECT ROUND(SUM(payment_value)::numeric, 2) FROM order_payments) AS total_paid
FROM order_items;

-- 2.10 Sparse months (why KPIs use Jan 2017 - Aug 2018)
SELECT DATE_TRUNC('month', order_purchase_timestamp)::date AS month, COUNT(*) AS orders
FROM orders GROUP BY 1 ORDER BY 1;
