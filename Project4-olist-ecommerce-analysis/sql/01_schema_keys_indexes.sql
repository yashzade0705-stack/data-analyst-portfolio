-- PostgreSQL. Run ONCE after scripts/load_data.py.
-- If a PRIMARY KEY fails, that table has duplicate IDs: note it in your README as a data-quality finding.

ALTER TABLE orders    ADD PRIMARY KEY (order_id);
ALTER TABLE customers ADD PRIMARY KEY (customer_id);
ALTER TABLE products  ADD PRIMARY KEY (product_id);
ALTER TABLE sellers   ADD PRIMARY KEY (seller_id);

CREATE INDEX IF NOT EXISTS idx_orders_cust    ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status  ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_items_order    ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_items_product  ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_items_seller   ON order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_pay_order      ON order_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_rev_order      ON order_reviews(order_id);
CREATE INDEX IF NOT EXISTS idx_cust_unique    ON customers(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_prod_cat       ON products(product_category_name);
