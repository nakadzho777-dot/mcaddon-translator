
import json
import os
from datetime import datetime

LOG_FILE = "data/logs.json"


# =========================
# 初期化
# =========================
def init_logs():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)


# =========================
# ログ追加
# =========================
def add_log(username: str, action: str, detail: dict = None):

    if detail is None:
        detail = {}

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append({
        "username": username,
        "action": action,
        "detail": detail,
        "time": datetime.utcnow().isoformat()
    })

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# =========================
# ログ取得
# =========================
def get_logs(limit: int = 100):

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    return logs[-limit:]