import json
import os
from datetime import datetime

from core.logger import log_event

ALERT_FILE = "logs/alerts.json"


# =========================
# アラート送信
# =========================
def trigger_alert(level: str, message: str, metadata: dict = None):
    os.makedirs("logs", exist_ok=True)

    alert = {
        "time": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "metadata": metadata or {}
    }

    alerts = load_alerts()
    alerts.append(alert)

    save_alerts(alerts)

    log_event(f"ALERT {level} {message}")

    # 仮：外部通知（拡張ポイント）
    notify(alert)


# =========================
# ロード
# =========================
def load_alerts():
    if not os.path.exists(ALERT_FILE):
        return []

    try:
        with open(ALERT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =========================
# 保存
# =========================
def save_alerts(data):
    with open(ALERT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 通知処理（拡張用）
# =========================
def notify(alert: dict):
    level = alert["level"]

    # ここをSlack / Discord / Emailに拡張できる
    if level == "CRITICAL":
        print(f"[CRITICAL ALERT] {alert['message']}")

    elif level == "WARNING":
        print(f"[WARNING] {alert['message']}")


# =========================
# 最新アラート取得
# =========================
def get_recent_alerts(limit: int = 10):
    alerts = load_alerts()
    return alerts[-limit:]