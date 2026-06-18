import json
import os
from datetime import datetime

from core.logger import log_event

AUDIT_LOG = "logs/audit_log.json"


# =========================
# ログ追加
# =========================
def record_action(user_id: str, action: str, target: str = None, metadata: dict = None):
    os.makedirs("logs", exist_ok=True)

    entry = {
        "time": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "target": target,
        "metadata": metadata or {}
    }

    if os.path.exists(AUDIT_LOG):
        with open(AUDIT_LOG, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    else:
        logs = []

    logs.append(entry)

    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    log_event(f"AUDIT {action} {user_id}")


# =========================
# 履歴取得
# =========================
def get_user_history(user_id: str):
    if not os.path.exists(AUDIT_LOG):
        return []

    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        logs = json.load(f)

    return [log for log in logs if log.get("user_id") == user_id]


# =========================
# 全体ログ取得
# =========================
def get_all_logs(limit: int = 100):
    if not os.path.exists(AUDIT_LOG):
        return []

    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        logs = json.load(f)

    return logs[-limit:]


# =========================
# 不審行動検知
# =========================
def detect_anomalies(user_id: str):
    logs = get_user_history(user_id)

    actions = [l["action"] for l in logs]

    suspicious = []

    if actions.count("deploy") > 5:
        suspicious.append("HIGH_DEPLOY_FREQUENCY")

    if actions.count("rollback") > 3:
        suspicious.append("ROLLBACK_LOOP")

    return {
        "user_id": user_id,
        "suspicious": suspicious,
        "risk": "HIGH" if suspicious else "LOW"
    }