-- PostgreSQL. KPI queries - each block starts with "-- name: <file name>" so scripts/run_sql_export.py can export it.
-- Revenue = SUM(item price), excluding freight, delivered orders only. KPI window = Jan 2017 - Aug 2018.

-- name: k1_monthly_revenue
SELECT DATE_TRUNC('month', o.order_purchase_timestamp)::date AS month,
       ROUND(SUM(i.price)::numeric, 2)                       AS revenue,
       COUNT(DISTINCT o.order_id)                            AS orders,
       ROUND((SUM(i.price) / COUNT(DISTINCT o.order_id))::numeric, 2) AS aov
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01' AND o.order_purchase_timestamp < '2018-09-01'
GROUP BY 1
ORDER BY 1;

-- name: k2_mom_growth
WITH m AS (
  SELECT DATE_TRUNC('month', o.order_purchase_timestamp)::date AS month, SUM(i.price) AS revenue
  FROM orders o JOIN order_items i ON o.order_id = i.order_id
  WHERE o.order_status = 'delivered'
    AND o.order_purchase_timestamp >= '2017-01-01' AND o.order_purchase_timestamp < '2018-09-01'
  GROUP BY 1
)
SELECT month,
       ROUND(revenue::numeric, 2) AS revenue,
       ROUND((100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month))::numeric, 1) AS mom_growth_pct
FROM m ORDER BY month;

-- name: k3_top_categories
SELECT COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
       ROUND(SUM(i.price)::numeric, 2) AS revenue,
       COUNT(DISTINCT o.order_id)      AS orders
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
JOIN products p    ON i.product_id = p.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
  AND o.order_purchase_timestamp >= '2017-01-01' AND o.order_purchase_timestamp < '2018-09-01'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 15;

-- name: k4_delivery_days_by_state
SELECT c.customer_state,
       COUNT(*) AS orders,
       ROUND(AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400)::numeric, 1) AS avg_delivery_days,
       ROUND(100.0 * AVG((o.order_delivered_customer_date > o.order_estimated_delivery_date)::int), 1) AS late_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1
ORDER BY 3 DESC;

-- name: k5_review_by_lateness
WITH r AS (SELECT order_id, AVG(review_score) AS score FROM order_reviews GROUP BY 1)
SELECT CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late' ELSE 'On time' END AS delivery_status,
       COUNT(*) AS orders,
       ROUND(AVG(r.score)::numeric, 2) AS avg_review
FROM orders o JOIN r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- name: k6_payment_type_mix
SELECT payment_type,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(payment_value)::numeric, 2) AS paid,
       ROUND(100.0 * SUM(payment_value) / SUM(SUM(payment_value)) OVER (), 1) AS pct_of_paid
FROM order_payments
GROUP BY 1 ORDER BY 3 DESC;

-- name: k7_revenue_by_state
SELECT c.customer_state,
       ROUND(SUM(i.price)::numeric, 2) AS revenue,
       COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
JOIN customers c   ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 1 ORDER BY 2 DESC;

-- name: k8_repeat_customers
WITH per AS (
  SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n_orders
  FROM orders o JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY 1
)
SELECT COUNT(*) AS customers,
       SUM((n_orders >= 2)::int) AS repeat_customers,
       ROUND(100.0 * AVG((n_orders >= 2)::int), 2) AS repeat_pct
FROM per;

-- name: k9_seller_concentration
WITH s AS (
  SELECT i.seller_id, SUM(i.price) AS revenue
  FROM order_items i JOIN orders o ON i.order_id = o.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY 1
), ranked AS (
  SELECT seller_id, revenue,
         RANK() OVER (ORDER BY revenue DESC) AS rnk,
         100.0 * revenue / SUM(revenue) OVER () AS share_pct
  FROM s
)
SELECT rnk, seller_id, ROUND(revenue::numeric, 2) AS revenue, ROUND(share_pct::numeric, 2) AS share_pct,
       ROUND(SUM(share_pct) OVER (ORDER BY rnk)::numeric, 1) AS cum_share_pct
FROM ranked
WHERE rnk <= 20
ORDER BY rnk;

-- name: k10_weekday_pattern
SELECT EXTRACT(ISODOW FROM o.order_purchase_timestamp)::int AS weekday_num,
       TO_CHAR(o.order_purchase_timestamp, 'Dy') AS weekday,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(i.price)::numeric, 2) AS revenue
FROM orders o JOIN order_items i ON o.order_id = i.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1, 2 ORDER BY 1;

-- name: k11_review_distribution
SELECT review_score, COUNT(*) AS reviews,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM order_reviews
GROUP BY 1 ORDER BY 1;

-- name: k12_cancel_rate_by_month
-- Uses the orders table directly (NOT an items join) so orders without items are counted.
SELECT DATE_TRUNC('month', order_purchase_timestamp)::date AS month,
       COUNT(*) AS orders,
       ROUND(100.0 * AVG((order_status = 'canceled')::int), 2) AS cancel_pct
FROM orders
WHERE order_purchase_timestamp >= '2017-01-01' AND order_purchase_timestamp < '2018-09-01'
GROUP BY 1 ORDER BY 1;
