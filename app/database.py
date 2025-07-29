import sqlite3
import pathlib
from fastapi import HTTPException

DB_PATH = pathlib.Path(__file__).parent / "data/data.db"

# Data Access Layer for API
"""Database Functions Provided:
    1. create user
    2 create job
    3. Update job
    4. get result_text from job
    5. update user llm tokens
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_user(user_id: str, email: str, password_hash: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)", (user_id, email, password_hash))
            conn.commit()
            return user_id
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except sqlite3.Error as e:
        print(f"Database error (create_user): {e}")
    finally:
        conn.close()
    return None


def get_user_by_email(email: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
            row = cur.fetchone()
            return row if row else None
    except sqlite3.Error as e:
        print(f"Database error (get_user_by_email): {e}")
    finally:
        conn.close()
    return None


def update_user_auth_jwt(user_id: str, auth_jwt: str):
    try:
        user_id = int(user_id)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET auth_jwt = ? WHERE id = ?",
                (auth_jwt, user_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error (update_user_auth_jwt): {e}")
    finally:
        conn.close()


def update_tokens_by_user_id(user_id: str, tokens: int):
    try:
        user_id = int(user_id)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET tokens = ? WHERE id = ?",
                (tokens, user_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error (update_tokens_by_user_id): {e}")


def create_job(job_id: str, user_id: int, input_text: str, result_text: str = None):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO jobs (id, user_id, input_text, result_text) VALUES (?, ?, ?, ?)",
                (job_id, user_id, input_text, result_text)
            )
            job_id = cur.lastrowid
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Database error (create_job): {e}")
        return False


def update_job(job_id: str, result_text: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET result_text = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (result_text, job_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error (update_job): {e}")


def job_exists(job_id: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM jobs WHERE id = ? LIMIT 1", (job_id,))
            return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Database error (job_exists): {e}")


def get_result_text_by_job_id(job_id: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT result_text FROM jobs WHERE id = ?",
                (job_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Database error (get_result_text_by_job_id): {e}")


if __name__ == "__main__":
    create_user("test_user@gmail.com")
