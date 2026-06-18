import json
import os
from datetime import datetime

from core.logger import log_event

ALERT_LOG = "logs/alerts.json"


# =========================
# アラート発火
# =========================
def trigger_alert(level: str, message: str, context: dict = None):
    os.makedirs("logs", exist_ok=True)

    alert = {
        "time": datetime.now().isoformat(),
        "level": level,  # INFO / WARNING / CRITICAL
        "message": message,
        "context": context or {}
    }

    if os.path.exists(ALERT_LOG):
        with open(ALERT_LOG, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    else:
        logs = []

    logs.append(alert)

    with open(ALERT_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    log_event(f"ALERT {level} {message}")


# =========================
# 重要度判定
# =========================
def evaluate_severity(score: int):
    if score >= 90:
        return "CRITICAL"
    elif score >= 70:
        return "WARNING"
    else:
        return "INFO"


# =========================
# システム異常検知
# =========================
def check_system_anomalies(metrics: dict):
    alerts = []

    if metrics.get("error_rate", 0) > 0.1:
        alerts.append(("CRITICAL", "ERROR_RATE_HIGH"))

    if metrics.get("response_time", 0) > 3000:
        alerts.append(("WARNING", "SLOW_RESPONSE"))

    if metrics.get("cpu_usage", 0) > 90:
        alerts.append(("WARNING", "HIGH_CPU"))

    for level, msg in alerts:
        trigger_alert(level, msg, metrics)

    return alerts


# =========================
# 通知（ダミー実装）
# =========================
def notify_admin(message: str):
    # 本番では Slack / Discord / Email に置き換え
    print(f"[NOTIFY] {message}")

    log_event(f"NOTIFY_SENT {message}")