from nvr_proto.db import get_db_connection

MASTERY_ACCURACY = 0.80
MASTERY_MIN_ATTEMPTS = 10


def get_or_create_user(email: str, name: str | None = None) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM nvr_users WHERE email=%s", (email,))
            row = cur.fetchone()
            if row:
                return int(row[0])

            cur.execute(
                "INSERT INTO nvr_users(email, name) VALUES(%s,%s) RETURNING id",
                (email, name),
            )
            uid = cur.fetchone()[0]
            conn.commit()
            return int(uid)
    finally:
        conn.close()


def record_attempt(
    user_id: int,
    pattern_id: str,
    family: str,
    level: int,
    is_correct: bool,
    duration_ms: int | None,
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO nvr_attempts(user_id, pattern_id, family, level, is_correct, duration_ms)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (user_id, pattern_id, family, level, is_correct, duration_ms),
            )
            conn.commit()
    finally:
        conn.close()


def get_level_stats(user_id: int, family: str, level: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  COUNT(*) as n,
                  AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) as acc
                FROM nvr_attempts
                WHERE user_id=%s AND family=%s AND level=%s
                """,
                (user_id, family, level),
            )
            n, acc = cur.fetchone()
            n = int(n or 0)
            acc = float(acc or 0.0)
            return n, acc
    finally:
        conn.close()


def is_level_mastered(user_id: int, family: str, level: int) -> bool:
    n, acc = get_level_stats(user_id, family, level)
    return n >= MASTERY_MIN_ATTEMPTS and acc >= MASTERY_ACCURACY


def get_unlocked_level(user_id: int, family: str, max_level: int = 5) -> int:
    # unlocked = highest consecutive mastered + 1 (capped)
    unlocked = 1
    for lvl in range(1, max_level + 1):
        if is_level_mastered(user_id, family, lvl):
            unlocked = min(lvl + 1, max_level)
        else:
            break
    return unlocked
