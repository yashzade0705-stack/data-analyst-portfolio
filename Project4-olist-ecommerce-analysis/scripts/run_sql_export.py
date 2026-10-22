"""Run every named query in sql/03_kpi_queries.sql and save each result as a CSV in results/sql/.

Queries are separated by lines like:  -- name: k1_monthly_revenue
Needs the database loaded (scripts/load_data.py) and OLIST_DB_URL set.
"""
import re
from pathlib import Path

import pandas as pd

from db import get_engine

ROOT = Path(__file__).resolve().parents[1]
SQL_FILE = ROOT / "sql" / "03_kpi_queries.sql"
OUT = ROOT / "results" / "sql"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    engine = get_engine()
    text = SQL_FILE.read_text()
    parts = re.split(r"^-- name:\s*(\S+)\s*$", text, flags=re.M)
    # parts = [preamble, name1, sql1, name2, sql2, ...]
    for name, sql in zip(parts[1::2], parts[2::2]):
        sql = sql.strip().rstrip(";")
        df = pd.read_sql(sql, engine)
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"{name:32s} {len(df):>6,} rows")


if __name__ == "__main__":
    main()
