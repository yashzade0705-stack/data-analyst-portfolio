-- Project 3: E-commerce funnel analysis (Retailrocket events)
-- Written for SQLite. Table `events` columns: timestamp (ms since 1970), visitorid, event, itemid, transactionid
-- event is one of: view, addtocart, transaction
-- Each block starts with "-- name: <result file name>" and ends with a semicolon.

-- name: q1_funnel
-- Strict funnel: a visitor counts at a step only if they also reached the step before it.
WITH flags AS (
    SELECT visitorid,
           MAX(CASE WHEN event = 'view'        THEN 1 ELSE 0 END) AS viewed,
           MAX(CASE WHEN event = 'addtocart'   THEN 1 ELSE 0 END) AS carted,
           MAX(CASE WHEN event = 'transaction' THEN 1 ELSE 0 END) AS bought
    FROM events
    GROUP BY visitorid
),
steps AS (
    SELECT 1 AS step_no, '1: Viewed a product' AS step, SUM(viewed) AS visitors FROM flags
    UNION ALL
    SELECT 2, '2: Added to cart', SUM(CASE WHEN viewed = 1 AND carted = 1 THEN 1 ELSE 0 END) FROM flags
    UNION ALL
    SELECT 3, '3: Purchased', SUM(CASE WHEN viewed = 1 AND carted = 1 AND bought = 1 THEN 1 ELSE 0 END) FROM flags
)
SELECT step_no,
       step,
       visitors,
       ROUND(100.0 * visitors / FIRST_VALUE(visitors) OVER (ORDER BY step_no), 2)  AS pct_of_all_viewers,
       ROUND(100.0 * visitors / LAG(visitors) OVER (ORDER BY step_no), 2)          AS pct_of_previous_step,
       ROUND(100.0 - 100.0 * visitors / LAG(visitors) OVER (ORDER BY step_no), 2)  AS dropoff_pct
FROM steps
ORDER BY step_no;

-- name: q2_daily
-- Daily visitors per step and view-to-purchase conversion.
SELECT date(timestamp / 1000, 'unixepoch')                                 AS day,
       COUNT(DISTINCT CASE WHEN event = 'view'        THEN visitorid END)  AS viewers,
       COUNT(DISTINCT CASE WHEN event = 'addtocart'   THEN visitorid END)  AS cart_visitors,
       COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)  AS buyers,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
             / NULLIF(COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END), 0), 2) AS view_to_buy_pct
FROM events
GROUP BY 1
ORDER BY 1;

-- name: q3_top_items
-- The 20 most viewed items and how well each one converts.
SELECT itemid,
       COUNT(DISTINCT CASE WHEN event = 'view'        THEN visitorid END) AS viewers,
       COUNT(DISTINCT CASE WHEN event = 'addtocart'   THEN visitorid END) AS cart_visitors,
       COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END) AS buyers,
       ROUND(100.0 * COUNT(DISTINCT CASE WHEN event = 'addtocart' THEN visitorid END)
             / NULLIF(COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END), 0), 2) AS view_to_cart_pct
FROM events
GROUP BY itemid
ORDER BY viewers DESC
LIMIT 20;

-- name: q4_time_to_purchase
-- Hours from a buyer's first event to their first purchase, grouped into time bands.
WITH firsts AS (
    SELECT visitorid,
           MIN(timestamp) AS first_event,
           MIN(CASE WHEN event = 'transaction' THEN timestamp END) AS first_purchase
    FROM events
    GROUP BY visitorid
),
buyers AS (
    SELECT visitorid, (first_purchase - first_event) / 3600000.0 AS hours_to_buy
    FROM firsts
    WHERE first_purchase IS NOT NULL
)
SELECT CASE WHEN hours_to_buy < 1   THEN '1: Within 1 hour'
            WHEN hours_to_buy < 24  THEN '2: 1 to 24 hours'
            WHEN hours_to_buy < 168 THEN '3: 1 to 7 days'
            ELSE                         '4: Over 7 days' END AS time_band,
       COUNT(*)                                               AS buyers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)     AS pct_of_buyers
FROM buyers
GROUP BY 1
ORDER BY 1;

-- name: q5_event_totals
-- Overall size of the data set.
SELECT event,
       COUNT(*)                   AS events,
       COUNT(DISTINCT visitorid)  AS visitors
FROM events
GROUP BY event
ORDER BY events DESC;
