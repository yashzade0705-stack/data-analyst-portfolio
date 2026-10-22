"""One place for the database connection. The password never lives in code.

Set the environment variable once in your terminal (PostgreSQL example):

    Windows (PowerShell):  $env:OLIST_DB_URL = "postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/olist"
    Mac / Linux:           export OLIST_DB_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/olist"

If your password has special characters (@ : /), URL-encode them (@ -> %40).
"""
import os

from sqlalchemy import create_engine


def get_engine():
    url = os.environ.get("OLIST_DB_URL")
    if not url:
        raise SystemExit(
            "OLIST_DB_URL is not set. See the docstring in scripts/db.py for how to set it."
        )
    return create_engine(url)
