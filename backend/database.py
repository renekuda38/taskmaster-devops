# backend/database.py
# postgres db connection

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")

    conn = psycopg2.connect(database_url, cursor_factory = RealDictCursor)

    return conn

def test_db_connection():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1")
        cur.fetchone()

        cur.close()
        conn.close()

        print("Database connection successful")
        return True

    except Exception as e:
        print(f"Database connection failed: {e}")
        return False