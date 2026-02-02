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
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS nvr_users (
          id SERIAL PRIMARY KEY,
          email TEXT UNIQUE NOT NULL,
          name TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS nvr_attempts (
          id SERIAL PRIMARY KEY,
          user_id INTEGER NOT NULL,
          pattern_id TEXT NOT NULL,
          family TEXT NOT NULL,
          level INTEGER NOT NULL,
          is_correct BOOLEAN NOT NULL,
          duration_ms INTEGER,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_nvr_attempts_user_family_level
        ON nvr_attempts(user_id, family, level);
        """,
    ]
    conn = get_db_connection()
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for statement in ddl:
                cur.execute(statement)
    finally:
        conn.close()
