import json
import os

USER_DB = "data/users.json"


# =========================
# ユーザー取得
# =========================
def load_users():
    if not os.path.exists(USER_DB):
        return {}

    with open(USER_DB, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 権限チェック
# =========================
def has_permission(user_id: str, action: str):
    users = load_users()

    user = users.get(user_id)

    if not user:
        return False

    role = user.get("plan", "free")

    permissions = {
        "free": ["view"],
        "pro": ["view", "generate", "rewrite", "seo"],
        "business": ["view", "generate", "rewrite", "seo", "admin"]
    }

    allowed = permissions.get(role, [])

    return action in allowed


# =========================
# 管理者判定
# =========================
def is_admin(user_id: str):
    users = load_users()

    user = users.get(user_id)

    if not user:
        return False

    return user.get("plan") == "business"


# =========================
# アクセス拒否チェック
# =========================
def enforce_permission(user_id: str, action: str):
    if not has_permission(user_id, action):
        raise PermissionError(f"❌ Permission denied: {action} for {user_id}")