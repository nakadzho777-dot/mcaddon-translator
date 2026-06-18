import json
import os
from datetime import datetime, timedelta

from core.logger import log_event

ANALYTICS_FILE = "data/analytics.json"


# =========================
# データロード
# =========================
def load_data():
    if not os.path.exists(ANALYTICS_FILE):
        return []

    try:
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =========================
# データ保存
# =========================
def save_data(data):
    os.makedirs("data", exist_ok=True)

    with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# イベント記録
# =========================
def track_event(user_id: str, event: str, metadata: dict = None):
    data = load_data()

    data.append({
        "time": datetime.now().isoformat(),
        "user_id": user_id,
        "event": event,
        "metadata": metadata or {}
    })

    save_data(data)

    log_event(f"TRACK {event}")


# =========================
# ユーザー数
# =========================
def get_active_users(days: int = 7):
    data = load_data()

    cutoff = datetime.now() - timedelta(days=days)

    users = {
        d["user_id"]
        for d in data
        if datetime.fromisoformat(d["time"]) > cutoff
    }

    return len(users)


# =========================
# イベント数
# =========================
def get_event_count(event_name: str):
    data = load_data()

    return len([d for d in data if d["event"] == event_name])


# =========================
# コンバージョン率
# =========================
def get_conversion_rate():
    data = load_data()

    total = len(data)
    if total == 0:
        return 0

    converted = len([d for d in data if "upgrade" in d["event"]])

    return converted / total


# =========================
# 成長スコア
# =========================
def get_growth_score():
    users = get_active_users()
    conv = get_conversion_rate()

    score = (users * 0.5) + (conv * 100)

    return round(score, 2)


# =========================
# レポート
# =========================
def get_analytics_report():
    return {
        "active_users_7d": get_active_users(),
        "conversion_rate": get_conversion_rate(),
        "growth_score": get_growth_score(),
        "total_events": len(load_data())
    }