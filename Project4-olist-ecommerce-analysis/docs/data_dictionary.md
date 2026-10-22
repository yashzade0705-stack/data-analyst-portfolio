# Data dictionary - tables in `dashboard_data/`

## fact_orders.csv (one row per order, all statuses)
| Column | Meaning |
|---|---|
| order_id | Unique order |
| customer_unique_id | The real customer (customer_id changes per order) |
| customer_state / customer_city | Delivery location |
| order_status | delivered, canceled, shipped, unavailable, ... |
| is_delivered | 1 if status = delivered |
| in_window | 1 if purchased Jan 2017 - Aug 2018 |
| purchase_date / month | Purchase day / first day of the month |
| items_revenue | Sum of item prices (excl. freight); blank if the order has no items |
| freight | Sum of freight values |
| payment_value | Total paid by the customer |
| n_items | Number of items |
| review_score | Average review score for the order (1-5) |
| delivery_days | Purchase -> delivered to customer |
| estimated_days | Purchase -> estimated delivery |
| delay_days | Delivered minus estimated (positive = late) |
| is_late | 1 late, 0 on time, blank if not delivered |

## fact_order_items.csv
order_id, order_item_id, product_id, seller_id, seller_state, category (English), price, freight_value

## customer_segments.csv (delivered orders, one row per customer)
customer_unique_id, orders, monetary (sum of item price), recency_days (to snapshot date), first/last purchase, segment

## Aggregated helper tables
kpi_monthly, category_revenue, state_delivery, seller_concentration, weekday_pattern, review_by_lateness, segment_summary, dim_date
