"""One-off script: creates the project's database on the shared Postgres server.

Postgres can't run CREATE DATABASE while connected to the database being created, so this
connects to an existing database on the same server (ADMIN_DATABASE_URL) instead.
"""

import os
import re

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()


def _dbname_from_url(url: str) -> str:
    return url.rsplit("/", 1)[-1]


def create_database() -> None:
    admin_url = os.environ["ADMIN_DATABASE_URL"]
    target_db = _dbname_from_url(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(admin_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            if cur.fetchone():
                print(f"Database '{target_db}' already exists.")
                return
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
            print(f"Database '{target_db}' created.")
    finally:
        conn.close()


if __name__ == "__main__":
    create_database()
