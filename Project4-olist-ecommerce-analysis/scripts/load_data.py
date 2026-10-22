"""Load the raw Olist CSVs into PostgreSQL (optional - the pandas pipeline does not need a database).

Usage:
    python scripts/load_data.py            # skips the big geolocation table
    python scripts/load_data.py --with-geo

Afterwards run sql/01_schema_keys_indexes.sql once in pgAdmin / psql.
"""
import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy.types import VARCHAR

from db import get_engine

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DATE_COLS = {
    "orders": [
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
}


def table_name(path: Path) -> str:
    return path.name.replace("olist_", "").replace("_dataset.csv", "").replace(".csv", "")


def main(with_geo: bool) -> None:
    engine = get_engine()
    for f in sorted(RAW.glob("*.csv")):
        name = table_name(f)
        if name == "geolocation" and not with_geo:
            print("skipped: geolocation (use --with-geo to load it)")
            continue
        df = pd.read_csv(f, parse_dates=DATE_COLS.get(name, []))
        dtype = {c: VARCHAR(50) for c in df.columns if df[c].dtype == object and c.endswith("_id")}
        df.to_sql(name, engine, if_exists="replace", index=False, dtype=dtype, chunksize=5000)
        print(f"loaded: {name:40s} {len(df):>9,} rows")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-geo", action="store_true")
    main(ap.parse_args().with_geo)
