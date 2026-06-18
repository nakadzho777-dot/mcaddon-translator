from core.logger import log_event
from core.rbac import get_user_role


# =========================
# 権限定義
# =========================
PERMISSIONS = {
    "user": ["read", "translate", "generate"],
    "pro": ["read", "translate", "generate", "seo"],
    "admin": ["read", "translate", "generate", "seo", "deploy", "admin"]
}


# =========================
# 権限チェック
# =========================
def has_permission(user_id: str, action: str):
    role = get_user_role(user_id)

    allowed = PERMISSIONS.get(role, [])

    return action in allowed


# =========================
# 強制実行ガード
# =========================
def enforce(user_id: str, action: str, func, *args, **kwargs):
    if not has_permission(user_id, action):
        log_event(f"ACCESS_DENIED {user_id} {action}", level="WARNING")

        return {
            "error": "ACCESS_DENIED",
            "action": action
        }

    try:
        result = func(*args, **kwargs)

        log_event(f"ACCESS_GRANTED {user_id} {action}")

        return result

    except Exception as e:
        log_event(f"SECURITY_ERROR {user_id} {e}", level="ERROR")

        return {
            "error": "EXECUTION_FAILED"
        }


# =========================
# ロール昇格チェック
# =========================
def can_escalate(user_id: str, target_role: str):
    role = get_user_role(user_id)

    if role != "admin":
        return False

    if target_role not in PERMISSIONS:
        return False

    return True


# =========================
# 不審アクセス検知
# =========================
def detect_suspicious_activity(user_id: str, action: str):
    role = get_user_role(user_id)

    if role == "user" and action in ["deploy", "admin"]:
        log_event(f"SUSPICIOUS_ACTIVITY {user_id} {action}", level="ERROR")
        return True

    return False