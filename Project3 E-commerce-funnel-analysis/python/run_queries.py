"""
Project 3 - E-commerce funnel analysis: run the SQL and save the results.
From the E-commerce-funnel-analysis folder:
    pip install pandas
    python python/run_queries.py
Needs : data/events.csv  (Retailrocket events file from Kaggle)
Writes: results/<name>.csv for every block in sql/01_funnel_analysis.sql
SQLite is built into Python, so nothing else needs installing.
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
EVENTS = BASE / "data" / "events.csv"
SQL_FILE = BASE / "sql" / "01_funnel_analysis.sql"
OUT = BASE / "results"
OUT.mkdir(exist_ok=True)

if not EVENTS.exists():
    raise SystemExit(f"Put events.csv at {EVENTS} and try again.")

con = sqlite3.connect(":memory:")

# Load the CSV in chunks so a 2.7 million row file does not use too much memory
total = 0
for chunk in pd.read_csv(EVENTS, chunksize=500_000):
    chunk.to_sql("events", con, if_exists="append", index=False)
    total += len(chunk)
print("Rows loaded from events.csv:", total)
con.execute("CREATE INDEX idx_events_visitor ON events(visitorid)")
con.execute("CREATE INDEX idx_events_item ON events(itemid)")

text = SQL_FILE.read_text(encoding="utf-8")
blocks = re.split(r"^-- name:\s*(\w+)\s*$", text, flags=re.MULTILINE)
# blocks = [preamble, name1, sql1, name2, sql2, ...]
for name, sql in zip(blocks[1::2], blocks[2::2]):
    df = pd.read_sql_query(sql, con)
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"\n=== {name} ===")
    print(df.to_string(index=False))
print("\nSaved result files to", OUT)
