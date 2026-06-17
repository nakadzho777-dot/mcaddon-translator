from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import time

app = FastAPI()

DB_PATH = "cloud.db"

# =========================
# DB初期化
# =========================
def init_db():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dictionary (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            score INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# モデル
# =========================
class Entry(BaseModel):
    key: str
    value: str
    user_id: str | None = None
    token: str | None = None


VALID_TOKEN = "MCADDON-DEV-TOKEN"


def check_token(token):
    if token != VALID_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


# =========================
# 辞書追加（＋ポイント付与）
# =========================
@app.post("/add")
def add(entry: Entry):

    check_token(entry.token)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 辞書保存
    cur.execute("""
        INSERT OR REPLACE INTO dictionary (key, value, updated_at)
        VALUES (?, ?, ?)
    """, (entry.key, entry.value, int(time.time())))

    # ユーザースコア加算
    if entry.user_id:

        cur.execute("""
            INSERT OR IGNORE INTO users (user_id, score)
            VALUES (?, 0)
        """, (entry.user_id,))

        cur.execute("""
            UPDATE users
            SET score = score + 1
            WHERE user_id = ?
        """, (entry.user_id,))

    conn.commit()
    conn.close()

    return {"status": "ok"}


# =========================
# 取得
# =========================
@app.get("/get/{key}")
def get(key: str):

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT value FROM dictionary WHERE key = ?", (key,))
    row = cur.fetchone()

    conn.close()

    return {"value": row[0] if row else None}


# =========================
# ランキング取得
# =========================
@app.get("/ranking")
def ranking():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, score
        FROM users
        ORDER BY score DESC
        LIMIT 50
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {"user_id": u, "score": s}
        for u, s in rows
    ]