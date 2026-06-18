import os
import json
from datetime import datetime

LOG_PATH = "logs/app.log"
JSON_LOG_PATH = "logs/logs.json"


def ensure_dir():
    os.makedirs("logs", exist_ok=True)


def log_event(event: str, level: str = "INFO"):
    ensure_dir()

    timestamp = datetime.now().isoformat()

    log_entry = {
        "time": timestamp,
        "level": level,
        "event": event
    }

    # ① テキストログ（人間用）
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {level} | {event}\n")

    # ② JSONログ（分析用）
    logs = []

    if os.path.exists(JSON_LOG_PATH):
        try:
            with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except:
            logs = []

    logs.append(log_entry)

    with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def log_error(event: str):
    log_event(event, level="ERROR")


def log_success(event: str):
    log_event(event, level="SUCCESS")