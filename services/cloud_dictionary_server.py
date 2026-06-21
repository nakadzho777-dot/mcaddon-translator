import os
import sqlite3
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


DB_PATH = os.getenv("DB_PATH", "cloud_dictionary.db")
API_KEY = os.getenv("CLOUD_DICTIONARY_API_KEY", "")

app = FastAPI(
    title="MCAddon Translator Cloud Dictionary",
    version="1.0.0"
)


class LookupRequest(BaseModel):
    source: str


class AddRequest(BaseModel):
    source: str
    translated: str


def now():
    return datetime.utcnow().isoformat()


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS dictionary (
            source TEXT PRIMARY KEY,
            translated TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    con.commit()
    con.close()


def check_api_key(x_api_key: str | None):
    if not API_KEY:
        return

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {
        "ok": True,
        "service": "MCAddon Translator Cloud Dictionary"
    }


@app.post("/lookup")
def lookup(req: LookupRequest):
    source = req.source.strip()

    if not source:
        return {
            "found": False,
            "translated": None
        }

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT translated FROM dictionary WHERE source = ?",
        (source,)
    )

    row = cur.fetchone()
    con.close()

    if not row:
        return {
            "found": False,
            "translated": None
        }

    return {
        "found": True,
        "translated": row[0]
    }


@app.post("/add")
def add(
    req: AddRequest,
    x_api_key: str | None = Header(default=None)
):
    check_api_key(x_api_key)

    source = req.source.strip()
    translated = req.translated.strip()

    if not source or not translated:
        return {
            "ok": False,
            "reason": "empty source or translated"
        }

    if len(source) > 5000 or len(translated) > 5000:
        return {
            "ok": False,
            "reason": "too long"
        }

    con = connect()
    cur = con.cursor()

    t = now()

    cur.execute(
        """
        INSERT INTO dictionary (
            source,
            translated,
            count,
            created_at,
            updated_at
        )
        VALUES (?, ?, 1, ?, ?)
        ON CONFLICT(source) DO UPDATE SET
            translated = excluded.translated,
            count = dictionary.count + 1,
            updated_at = excluded.updated_at
        """,
        (source, translated, t, t)
    )

    con.commit()
    con.close()

    return {
        "ok": True
    }


@app.get("/stats")
def stats():
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM dictionary")
    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT source, translated, count
        FROM dictionary
        ORDER BY count DESC
        LIMIT 20
        """
    )

    top = [
        {
            "source": row[0],
            "translated": row[1],
            "count": row[2]
        }
        for row in cur.fetchall()
    ]

    con.close()

    return {
        "total": total,
        "top": top
    }


@app.get("/export")
def export(
    x_api_key: str | None = Header(default=None)
):
    check_api_key(x_api_key)

    con = connect()
    cur = con.cursor()

    cur.execute(
        "SELECT source, translated FROM dictionary ORDER BY source ASC"
    )

    data = {
        row[0]: row[1]
        for row in cur.fetchall()
    }

    con.close()

    return data
