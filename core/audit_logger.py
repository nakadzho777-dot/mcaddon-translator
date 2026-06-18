import json
import os
from datetime import datetime

from core.logger import log_event


AUDIT_FILE = "logs/audit.json"


# =========================
# ロード
# =========================
def load_audit():
    if not os.path.exists(AUDIT_FILE):
        return []

    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


# =========================
# 保存
# =========================
def save_audit(data):
    os.makedirs("logs", exist_ok=True)

    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# 監査ログ記録
# =========================
def audit_log(user_id: str, action: str, target: str = "", metadata: dict = None):
    data = load_audit()

    entry = {
        "time": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "target": target,
        "metadata": metadata or {}
    }

    data.append(entry)

    save_audit(data)

    log_event(f"AUDIT {user_id} {action}")


# =========================
# ログ検索
# =========================
def search_audit(user_id: str = None, action: str = None):
    data = load_audit()

    result = data

    if user_id:
        result = [d for d in result if d["user_id"] == user_id]

    if action:
        result = [d for d in result if d["action"] == action]

    return result


# =========================
# 重要操作検出
# =========================
def detect_sensitive_actions():
    data = load_audit()

    sensitive = [
        d for d in data
        if d["action"] in ["delete", "export", "admin_change"]
    ]

    return sensitive


# =========================
# 監査レポート
# =========================
def audit_report():
    data = load_audit()

    return {
        "total_actions": len(data),
        "sensitive_actions": len(detect_sensitive_actions())
    }