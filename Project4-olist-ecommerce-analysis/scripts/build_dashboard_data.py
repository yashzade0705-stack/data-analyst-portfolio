"""
Build every dashboard-ready table from the raw Olist CSVs.

No database needed: this is pure pandas, so it runs on any laptop.
Output goes to dashboard_data/ (load these into Power BI / Excel / Tableau)
and a plain-English results/key_findings.md with the real numbers.

Usage (from the project root):
    python scripts/build_dashboard_data.py
    python scripts/build_dashboard_data.py --raw path/to/csvs --out path/to/out

Definitions used everywhere (state them in your README):
  * Revenue      = sum of item price, EXCLUDING freight, delivered orders only.
  * KPI window   = 2017-01-01 to 2018-08-31 (months outside it have a handful
                   of orders and distort growth charts).
  * Late order   = delivered to customer on a later calendar day than the estimated delivery date.
  * Segments     = rule-based "behavioral segmentation" (not quintile RFM,
                   because ~97% of customers bought only once).
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WINDOW_START, WINDOW_END = pd.Timestamp("2017-01-01"), pd.Timestamp("2018-08-31 23:59:59")

ORDER_DATES = [
    "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date",
]


def read(raw: Path, name: str, **kw) -> pd.DataFrame:
    path = raw / name
    if not path.exists():
        raise SystemExit(f"Missing file: {path}\nPut the Olist CSVs in {raw}")
    return pd.read_csv(path, **kw)


def build(raw: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)

    orders = read(raw, "olist_orders_dataset.csv", parse_dates=ORDER_DATES)
    customers = read(raw, "olist_customers_dataset.csv")
    items = read(raw, "olist_order_items_dataset.csv")
    pays = read(raw, "olist_order_payments_dataset.csv")
    reviews = read(raw, "olist_order_reviews_dataset.csv")
    products = read(raw, "olist_products_dataset.csv")
    sellers = read(raw, "olist_sellers_dataset.csv")
    trans = read(raw, "product_category_name_translation.csv")

    # ------------------------------------------------------------------ fact_orders
    # LEFT joins everywhere so orders with no items (cancelled / unavailable) are kept.
    item_agg = items.groupby("order_id").agg(
        items_revenue=("price", "sum"),
        freight=("freight_value", "sum"),
        n_items=("order_item_id", "count"),
    )
    pay_agg = pays.groupby("order_id").agg(payment_value=("payment_value", "sum"))
    rev_agg = reviews.groupby("order_id").agg(review_score=("review_score", "mean"))

    f = (
        orders.merge(customers[["customer_id", "customer_unique_id", "customer_state", "customer_city"]],
                     on="customer_id", how="left")
        .merge(item_agg, on="order_id", how="left")
        .merge(pay_agg, on="order_id", how="left")
        .merge(rev_agg, on="order_id", how="left")
    )
    f["purchase_date"] = f["order_purchase_timestamp"].dt.normalize()
    f["month"] = f["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    day = 86400.0
    f["delivery_days"] = (f["order_delivered_customer_date"] - f["order_purchase_timestamp"]).dt.total_seconds() / day
    f["estimated_days"] = (f["order_estimated_delivery_date"] - f["order_purchase_timestamp"]).dt.total_seconds() / day
    # The estimated delivery date has no time of day, so lateness is judged by calendar day:
    # delivered on the estimated day = on time.
    f["delay_days"] = (f["order_delivered_customer_date"].dt.normalize()
                       - f["order_estimated_delivery_date"].dt.normalize()).dt.days
    f["is_late"] = np.where(f["order_delivered_customer_date"].notna(),
                            (f["delay_days"] > 0).astype(float), np.nan)
    f["is_delivered"] = (f["order_status"] == "delivered").astype(int)
    f["in_window"] = f["order_purchase_timestamp"].between(WINDOW_START, WINDOW_END).astype(int)
    for c in ["items_revenue", "freight", "payment_value"]:
        f[c] = f[c].round(2)

    fact_cols = [
        "order_id", "customer_unique_id", "customer_state", "customer_city", "order_status",
        "is_delivered", "in_window", "purchase_date", "month", "items_revenue", "freight",
        "payment_value", "n_items", "review_score", "delivery_days", "estimated_days",
        "delay_days", "is_late",
    ]
    f[fact_cols].to_csv(out / "fact_orders.csv", index=False)

    d = f[(f["is_delivered"] == 1)]                      # delivered, all dates
    dw = d[d["in_window"] == 1]                          # delivered, KPI window

    # ------------------------------------------------------------------ fact_order_items
    prod = products[["product_id", "product_category_name"]].merge(trans, on="product_category_name", how="left")
    prod["category"] = prod["product_category_name_english"].fillna(prod["product_category_name"]).fillna("unknown")
    fi = (
        items.merge(prod[["product_id", "category"]], on="product_id", how="left")
        .merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")
    )
    fi["category"] = fi["category"].fillna("unknown")
    fi[["order_id", "order_item_id", "product_id", "seller_id", "seller_state", "category",
        "price", "freight_value"]].to_csv(out / "fact_order_items.csv", index=False)

    # ------------------------------------------------------------------ dim_date
    dates = pd.date_range(f["purchase_date"].min(), f["purchase_date"].max(), freq="D")
    dd = pd.DataFrame({"date": dates})
    dd["year"] = dd["date"].dt.year
    dd["quarter"] = "Q" + dd["date"].dt.quarter.astype(str)
    dd["month_num"] = dd["date"].dt.month
    dd["month_name"] = dd["date"].dt.strftime("%b")
    dd["month_start"] = dd["date"].dt.to_period("M").dt.to_timestamp()
    dd["year_month"] = dd["date"].dt.strftime("%Y-%m")
    dd["weekday_num"] = dd["date"].dt.dayofweek + 1
    dd["weekday"] = dd["date"].dt.strftime("%a")
    dd["in_window"] = dd["date"].between(WINDOW_START, WINDOW_END).astype(int)
    dd.to_csv(out / "dim_date.csv", index=False)

    # ------------------------------------------------------------------ KPI: monthly
    m = dw.groupby("month").agg(revenue=("items_revenue", "sum"), orders=("order_id", "nunique")).reset_index()
    m["aov"] = m["revenue"] / m["orders"]
    m["mom_growth_pct"] = m["revenue"].pct_change() * 100
    allw = f[f["in_window"] == 1].groupby("month").agg(
        all_orders=("order_id", "count"),
        cancelled=("order_status", lambda s: (s == "canceled").sum()),
    ).reset_index()
    allw["cancel_pct"] = 100 * allw["cancelled"] / allw["all_orders"]
    m = m.merge(allw[["month", "all_orders", "cancelled", "cancel_pct"]], on="month", how="left")
    num_cols = m.select_dtypes("number").columns
    m[num_cols] = m[num_cols].round(2)
    m.to_csv(out / "kpi_monthly.csv", index=False)

    # ------------------------------------------------------------------ categories
    ok_ids = set(dw["order_id"])
    fc = fi[fi["order_id"].isin(ok_ids)]
    cat = fc.groupby("category").agg(revenue=("price", "sum"), orders=("order_id", "nunique"),
                                     items=("order_id", "count"), avg_price=("price", "mean")).reset_index()
    cat["share_pct"] = 100 * cat["revenue"] / cat["revenue"].sum()
    cat = cat.sort_values("revenue", ascending=False).round(2)
    cat.to_csv(out / "category_revenue.csv", index=False)

    # ------------------------------------------------------------------ state delivery
    ds = d[d["delivery_days"].notna()]
    st = ds.groupby("customer_state").agg(
        orders=("order_id", "count"), avg_delivery_days=("delivery_days", "mean"),
        late_pct=("is_late", lambda s: 100 * s.mean()), avg_review=("review_score", "mean"),
        revenue=("items_revenue", "sum"),
    ).reset_index().sort_values("avg_delivery_days", ascending=False).round(2)
    st.to_csv(out / "state_delivery.csv", index=False)

    # ------------------------------------------------------------------ seller concentration
    sc = fc.groupby("seller_id").agg(revenue=("price", "sum"), orders=("order_id", "nunique")).reset_index()
    sc = sc.sort_values("revenue", ascending=False).reset_index(drop=True)
    sc["rank"] = sc.index + 1
    sc["share_pct"] = 100 * sc["revenue"] / sc["revenue"].sum()
    sc["cum_share_pct"] = sc["share_pct"].cumsum()
    sc.round(2).to_csv(out / "seller_concentration.csv", index=False)

    # ------------------------------------------------------------------ weekday
    w = dw.copy()
    w["weekday_num"] = w["order_purchase_timestamp"].dt.dayofweek + 1
    w["weekday"] = w["order_purchase_timestamp"].dt.strftime("%a")
    wk = w.groupby(["weekday_num", "weekday"]).agg(orders=("order_id", "nunique"),
                                                   revenue=("items_revenue", "sum")).reset_index().round(2)
    wk.to_csv(out / "weekday_pattern.csv", index=False)

    # ------------------------------------------------------------------ reviews vs lateness
    rl = ds[ds["review_score"].notna()].copy()
    rl["delivery_status"] = np.where(rl["is_late"] == 1, "Late", "On time")
    rbl = rl.groupby("delivery_status").agg(
        orders=("order_id", "count"), avg_review=("review_score", "mean"),
        pct_1_2_star=("review_score", lambda s: 100 * (s <= 2).mean()),
    ).reset_index().round(2)
    rbl.to_csv(out / "review_by_lateness.csv", index=False)

    # ------------------------------------------------------------------ behavioral segments
    cu = d.groupby("customer_unique_id").agg(
        orders=("order_id", "nunique"), monetary=("items_revenue", "sum"),
        first_purchase=("order_purchase_timestamp", "min"), last_purchase=("order_purchase_timestamp", "max"),
    ).reset_index()
    snapshot = d["order_purchase_timestamp"].max().normalize() + pd.Timedelta(days=1)
    cu["recency_days"] = (snapshot - cu["last_purchase"]).dt.days
    one = cu["orders"] == 1
    hv_cut = cu.loc[one, "monetary"].quantile(0.75)     # threshold among one-time buyers only
    seg = np.select(
        [~one, cu["monetary"] >= hv_cut, cu["recency_days"] <= 90],
        ["Repeat customer", "High-value one-time", "Recent one-time"],
        default="Lapsed one-time",
    )
    cu["segment"] = seg
    cu["monetary"] = cu["monetary"].round(2)
    cu[["customer_unique_id", "orders", "monetary", "recency_days", "first_purchase", "last_purchase",
        "segment"]].to_csv(out / "customer_segments.csv", index=False)
    ss = cu.groupby("segment").agg(customers=("customer_unique_id", "count"),
                                   revenue=("monetary", "sum")).reset_index()
    ss["customer_share_pct"] = 100 * ss["customers"] / ss["customers"].sum()
    ss["revenue_share_pct"] = 100 * ss["revenue"] / ss["revenue"].sum()
    ss = ss.sort_values("revenue", ascending=False).round(2)
    ss.to_csv(out / "segment_summary.csv", index=False)

    # ------------------------------------------------------------------ headline numbers
    late_pct = 100 * ds["is_late"].mean()
    rv = rl.groupby("delivery_status")["review_score"].mean()
    total_pay = pays["payment_value"].sum()
    total_items_freight = items["price"].sum() + items["freight_value"].sum()
    stats = {
        "orders_total": int(len(orders)),
        "unique_customers": int(customers["customer_unique_id"].nunique()),
        "delivered_orders": int(len(d)),
        "orders_without_items": int(f["items_revenue"].isna().sum()),
        "cancel_rate_pct_all": round(100 * (orders["order_status"] == "canceled").mean(), 2),
        "repeat_customers": int((cu["orders"] >= 2).sum()),
        "delivered_customers": int(len(cu)),
        "repeat_rate_pct": round(100 * (cu["orders"] >= 2).mean(), 2),
        "late_pct": round(float(late_pct), 2),
        "review_on_time": round(float(rv.get("On time", np.nan)), 2),
        "review_late": round(float(rv.get("Late", np.nan)), 2),
        "revenue_in_window": round(float(dw["items_revenue"].sum()), 2),
        "payment_total": round(float(total_pay), 2),
        "items_plus_freight_total": round(float(total_items_freight), 2),
        "payment_gap_pct": round(100 * (total_pay - total_items_freight) / total_items_freight, 2),
        "snapshot_date": str(snapshot.date()),
        "top_category": str(cat.iloc[0]["category"]),
        "top_category_share_pct": round(float(cat.iloc[0]["share_pct"]), 1),
        "top10_seller_share_pct": round(float(sc.head(10)["share_pct"].sum()), 1),
        "top_1pct_sellers_share_pct": round(float(sc.head(max(1, int(len(sc) * 0.01)))["share_pct"].sum()), 1),
        "slowest_state": str(st.iloc[0]["customer_state"]),
        "slowest_state_days": round(float(st.iloc[0]["avg_delivery_days"]), 1),
        "fastest_state": str(st.iloc[-1]["customer_state"]),
        "fastest_state_days": round(float(st.iloc[-1]["avg_delivery_days"]), 1),
    }
    for _, r in ss.iterrows():
        stats[f"seg_{r['segment']}_customers"] = int(r["customers"])
        stats[f"seg_{r['segment']}_revenue_share_pct"] = float(r["revenue_share_pct"])

    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "validation_summary.json").write_text(json.dumps(stats, indent=2))
    write_findings(stats, m)
    return stats


def write_findings(s: dict, monthly: pd.DataFrame) -> None:
    first, last = monthly.iloc[0], monthly.iloc[-1]
    growth = 100 * (last["revenue"] / first["revenue"] - 1)
    text = f"""# Key findings (auto-generated from your data)

Generated by `scripts/build_dashboard_data.py`. Every number below comes from the CSVs you ran it on.

| Metric | Value |
|---|---|
| Orders / unique customers | {s['orders_total']:,} / {s['unique_customers']:,} |
| Delivered orders | {s['delivered_orders']:,} |
| Revenue, Jan 2017 - Aug 2018 (item price, excl. freight) | R$ {s['revenue_in_window']:,.0f} |
| Monthly revenue, first vs last month in window | R$ {first['revenue']:,.0f} -> R$ {last['revenue']:,.0f} ({growth:+.0f}%) |
| Cancellation rate (all orders) | {s['cancel_rate_pct_all']}% |
| Late deliveries (delivered orders) | {s['late_pct']}% |
| Avg review, on-time vs late | {s['review_on_time']} vs {s['review_late']} |
| Repeat customers | {s['repeat_customers']:,} of {s['delivered_customers']:,} ({s['repeat_rate_pct']}%) |
| Top category | {s['top_category']} ({s['top_category_share_pct']}% of revenue) |
| Top 10 sellers' share of revenue | {s['top10_seller_share_pct']}% |
| Slowest / fastest state (avg delivery days) | {s['slowest_state']} {s['slowest_state_days']} / {s['fastest_state']} {s['fastest_state_days']} |
| Payments vs items+freight gap | {s['payment_gap_pct']}% |

## Draft headline story
1. Growth: monthly revenue changed {growth:+.0f}% between {first['month']:%b %Y} and {last['month']:%b %Y}.
2. Retention is the opportunity: only {s['repeat_rate_pct']}% of customers ever bought again.
3. Delivery drives satisfaction: late orders average {s['review_late']} stars vs {s['review_on_time']} on time.
   (An association - the stats notebook tests it; it does not prove lateness caused the low scores.)

Snapshot date used for recency: {s['snapshot_date']}.
"""
    (ROOT / "results" / "key_findings.md").write_text(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(ROOT / "data" / "raw"))
    ap.add_argument("--out", default=str(ROOT / "dashboard_data"))
    a = ap.parse_args()
    res = build(Path(a.raw), Path(a.out))
    print(json.dumps(res, indent=2))
    print("\nDone. Tables are in", a.out, "- summary in results/key_findings.md")
