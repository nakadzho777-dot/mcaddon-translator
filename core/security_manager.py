from core.logger import log_event


# =========================
# 権限定義
# =========================
ROLES = {
    "guest": [],
    "user": ["read"],
    "pro": ["read", "translate", "export"],
    "admin": ["read", "translate", "export", "manage", "billing"]
}


# =========================
# 権限チェック
# =========================
def has_permission(user_role: str, action: str):
    allowed = ROLES.get(user_role, [])

    return action in allowed


# =========================
# アクセス制御実行
# =========================
def authorize(user_id: str, user_role: str, action: str):
    if not has_permission(user_role, action):
        log_event(f"ACCESS_DENIED {user_id} {action}", level="WARNING")

        return {
            "status": "denied",
            "reason": "insufficient_permissions"
        }

    log_event(f"ACCESS_GRANTED {user_id} {action}")

    return {
        "status": "allowed"
    }


# =========================
# 管理操作ガード
# =========================
def admin_only(user_role: str):
    return user_role == "admin"


# =========================
# 重要操作チェック
# =========================
def critical_action_guard(user_role: str, action: str):
    critical_actions = ["delete_project", "reset_db", "refund", "change_plan"]

    if action in critical_actions and user_role != "admin":
        return False

    return True