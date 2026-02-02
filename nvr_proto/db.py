import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(url)


def init_nvr_tables():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS nvr_users (
                  id SERIAL PRIMARY KEY,
                  email TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS nvr_attempts (
                  id SERIAL PRIMARY KEY,
                  user_id INTEGER,
                  pattern_id TEXT,
                  family TEXT,
                  level INTEGER,
                  is_correct BOOLEAN,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()
    finally:
        conn.close()
