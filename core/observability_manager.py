import os
import json
import traceback
from datetime import datetime

from core.logger import log_event

ALERT_LOG = "logs/alerts.json"


# =========================
# エラー記録
# =========================
def record_error(context: str, error: Exception):
    os.makedirs("logs", exist_ok=True)

    data = {
        "time": datetime.now().isoformat(),
        "context": context,
        "error": str(error),
        "trace": traceback.format_exc()
    }

    if os.path.exists(ALERT_LOG):
        with open(ALERT_LOG, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(data)

    with open(ALERT_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    log_event(f"ALERT {context} {error}")


# =========================
# 健康チェック
# =========================
def health_check(checks: dict):
    results = {}

    for name, func in checks.items():
        try:
            func()
            results[name] = "ok"

        except Exception as e:
            results[name] = f"fail: {str(e)}"
            record_error(name, e)

    return results


# =========================
# 自動復旧トリガー
# =========================
def auto_recover(system_restart_func):
    try:
        system_restart_func()
        log_event("AUTO_RECOVERY_SUCCESS")

    except Exception as e:
        record_error("AUTO_RECOVERY_FAIL", e)


# =========================
# 監視レポート
# =========================
def generate_alert_report():
    if not os.path.exists(ALERT_LOG):
        return []

    with open(ALERT_LOG, "r", encoding="utf-8") as f:
        return json.load(f)