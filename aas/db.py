import os
import psycopg2

def get_conn():
    db = os.getenv("DATABASE_URL")
    if not db:
        raise RuntimeError("DATABASE_URL not set")
    conn = psycopg2.connect(db)
    conn.autocommit = True
    return conn
