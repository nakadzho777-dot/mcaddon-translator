import json
import os
from datetime import datetime

DB_PATH = "data/generated_articles.json"


def ensure_db():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def load_db():
    ensure_db()

    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    ensure_db()

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_generated(keyword: str) -> bool:
    data = load_db()
    return keyword in data


def mark_generated(keyword: str, filename: str, score: int):
    data = load_db()

    data[keyword] = {
        "filename": filename,
        "score": score,
        "generated_at": datetime.now().isoformat()
    }

    save_db(data)


def get_generated_files():
    data = load_db()

    return [
        item["filename"]
        for item in data.values()
        if item.get("filename")
    ]