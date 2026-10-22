# Power BI dashboard - build guide (about 90 minutes)

Everything you need is already in `dashboard_data/`. Power BI Desktop is free (Windows). On a Mac use the web
version or Tableau Public - the same tables work; only the DAX syntax differs.

## 1. Import
**Home > Get data > Text/CSV**, load these 5 files from `dashboard_data/`, then **Transform data** to check types:

| Table | Key columns | Notes |
|---|---|---|
| `fact_orders` | order_id, purchase_date | ALL orders (all statuses). `purchase_date` = Date, `is_late` = Decimal (blank = not delivered) |
| `fact_order_items` | order_id | price, freight_value, category, seller_id |
| `dim_date` | date | `date` = Date; use `in_window` to keep Jan 2017 - Aug 2018 |
| `customer_segments` | customer_unique_id | one row per customer, has `segment` |
| `state_delivery` | customer_state | optional (pre-aggregated; for checking numbers) |

## 2. Model (Model view - drag to create relationships)
- `dim_date[date]` 1 -> * `fact_orders[purchase_date]`
- `fact_orders[order_id]` 1 -> * `fact_order_items[order_id]` (single direction, from orders to items)
- `customer_segments[customer_unique_id]` 1 -> * `fact_orders[customer_unique_id]`

Mark `dim_date` as a date table (Table tools > Mark as date table > `date`).
Hide the key columns from Report view.

## 3. Measures (Modeling > New measure)
```DAX
Revenue =
CALCULATE ( SUM ( fact_order_items[price] ), fact_orders[order_status] = "delivered" )

Orders =
CALCULATE ( DISTINCTCOUNT ( fact_orders[order_id] ), fact_orders[order_status] = "delivered" )

AOV = DIVIDE ( [Revenue], [Orders] )

Revenue Last Month =
CALCULATE ( [Revenue], DATEADD ( dim_date[date], -1, MONTH ) )

Revenue MoM % = DIVIDE ( [Revenue] - [Revenue Last Month], [Revenue Last Month] )

Avg Review = AVERAGE ( fact_orders[review_score] )

Avg Delivery Days =
CALCULATE ( AVERAGE ( fact_orders[delivery_days] ), fact_orders[order_status] = "delivered" )

Late Delivery % =
DIVIDE (
    CALCULATE ( COUNTROWS ( fact_orders ), fact_orders[is_late] = 1 ),
    CALCULATE ( COUNTROWS ( fact_orders ), NOT ISBLANK ( fact_orders[is_late] ) )
)

Cancel Rate % =
DIVIDE (
    CALCULATE ( COUNTROWS ( fact_orders ), fact_orders[order_status] = "canceled" ),
    COUNTROWS ( fact_orders )
)

Customers = DISTINCTCOUNT ( customer_segments[customer_unique_id] )

Repeat Customer % =
DIVIDE (
    CALCULATE ( COUNTROWS ( customer_segments ), customer_segments[orders] >= 2 ),
    COUNTROWS ( customer_segments )
)
```
Put `dim_date[in_window] = 1` as a **report-level filter** so every page covers Jan 2017 - Aug 2018 only.

## 4. Report pages

**Page 1 - Executive overview** (one glance, the "so what")
- 5 KPI cards: Revenue, Orders, AOV, Late Delivery %, Avg Review
- Line chart: `dim_date[year_month]` x `Revenue` (add `Revenue MoM %` as a tooltip)
- Bar chart: top 10 `fact_order_items[category]` by Revenue
- Map or bar: `fact_orders[customer_state]` by Revenue
- Slicers: year, state

**Page 2 - Delivery and customer satisfaction**
- Bar: `customer_state` by `Avg Delivery Days` (sorted, top = slowest)
- Clustered column: Avg Review by on-time vs late (use a calculated column `Delivery Status = IF(fact_orders[is_late]=1,"Late","On time")`)
- Scatter: state, x = Avg Delivery Days, y = Avg Review, size = Orders
- Text box with the stats result: "Late orders score ~2 stars lower (Mann-Whitney p < 0.001) - association, not proof of cause."

**Page 3 - Customers and retention**
- Donut/bars: `customer_segments[segment]` by Customers and by revenue share
- Cards: Customers, Repeat Customer %
- Table: segment, customers, revenue, recommended action (Win-back / Reward / Nurture / Upsell)

## 5. Design rules (what makes it look senior)
- One accent color (blue `#2A6FDB`) + one alert color (orange `#E8743B`) + greys. No rainbow.
- Title each page with the **insight**, not the topic ("Late deliveries cost ~2 review stars"), not "Delivery page".
- Same slicer positions on every page; align everything to the grid; 16:9 canvas.
- Format: currency as R$ with no decimals, percentages with 1 decimal.

## 6. Check your numbers against the pandas output
Revenue, Orders and Late Delivery % in Power BI must match `results/key_findings.md` (same filters). If they don't,
the relationship direction or the `in_window` filter is the usual culprit.

## 7. Publish
- Screenshot each page into `images/` (e.g. `dashboard_overview.png`) and put them at the top of the README.
- File > Export > PDF, and **Publish to web** (free account) only if you are comfortable with it being public; the dataset is public.
- Save the `.pbix` in this `dashboard/` folder.
