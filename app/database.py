import sqlite3
import datetime

DB_PATH = "./data/data.db"

# Data Access Layer for API
"""Database Functions Provided:
    1. create user
    2 create job
    3. Update job
    4. get result_text from job
    5. update user tokens
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_user(email: str, login_method: str = "None"):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO users (email, login_method) VALUES (?, ?)", (email, login_method))
            user_id = cur.lastrowid
            conn.commit()
            return user_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")


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
        print(f"Database error: {e}")


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
            return job_id
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def update_job(job_id: str, result_text: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET result_text = ?, updated_at = ? WHERE id = ?",
                (result_text, datetime.utcnow(), job_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def job_exists(job_id: str):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM jobs WHERE id = ? LIMIT 1", (job_id))
            return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Database error: {e}")


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
        print(f"Database error: {e}")


if __name__ == "__main__":
    create_user("test_user@gmail.com")
