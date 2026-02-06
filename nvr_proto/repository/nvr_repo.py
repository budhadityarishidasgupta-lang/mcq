import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any


def _get_conn():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(db_url)


def init_nvr_tables() -> None:
    """
    Idempotent schema init for NVR attempts. Safe to call on every app run.
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS nvr_attempts (
        id BIGSERIAL PRIMARY KEY,
        session_id TEXT NOT NULL,
        user_id TEXT NULL,

        pattern_family TEXT NOT NULL,
        difficulty TEXT NOT NULL,

        selected_index INT NOT NULL,
        correct_index INT NOT NULL,
        is_correct BOOLEAN NOT NULL,

        response_ms INT NOT NULL,

        ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_nvr_attempts_session_ts
        ON nvr_attempts (session_id, ts DESC);

    CREATE INDEX IF NOT EXISTS idx_nvr_attempts_user_ts
        ON nvr_attempts (user_id, ts DESC);

    CREATE INDEX IF NOT EXISTS idx_nvr_attempts_pattern
        ON nvr_attempts (pattern_family);
    """
    conn = _get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
    finally:
        conn.close()


def record_attempt(
    *,
    session_id: str,
    user_id: Optional[str],
    pattern_family: str,
    difficulty: str,
    selected_index: int,
    correct_index: int,
    is_correct: bool,
    response_ms: int,
) -> None:
    """
    Append-only attempt logging.
    """
    sql = """
    INSERT INTO nvr_attempts (
        session_id, user_id,
        pattern_family, difficulty,
        selected_index, correct_index, is_correct,
        response_ms
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    conn = _get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        session_id,
                        user_id,
                        pattern_family,
                        difficulty,
                        selected_index,
                        correct_index,
                        is_correct,
                        response_ms,
                    ),
                )
    finally:
        conn.close()


def get_session_summary(*, session_id: str) -> Dict[str, Any]:
    """
    Lightweight analytics for the current session.
    """
    sql = """
    SELECT
        COUNT(*) AS attempts,
        SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) AS correct,
        AVG(response_ms)::INT AS avg_response_ms
    FROM nvr_attempts
    WHERE session_id = %s
    """
    conn = _get_conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (session_id,))
                row = cur.fetchone() or {}
                return {
                    "attempts": int(row.get("attempts") or 0),
                    "correct": int(row.get("correct") or 0),
                    "avg_response_ms": int(row.get("avg_response_ms") or 0),
                }
    finally:
        conn.close()
