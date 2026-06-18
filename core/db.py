import os
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL", "saas.db")

def get_conn():
    # 本番はPostgreSQLに変更可能
    return sqlite3.connect("saas.db", check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        plan TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        name TEXT,
        description TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()