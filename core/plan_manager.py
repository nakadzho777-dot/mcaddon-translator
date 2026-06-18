import json
import os

USER_DB = "data/users.json"


# =========================
# ユーザー読み込み
# =========================
def load_users():
    if not os.path.exists(USER_DB):
        return {}

    with open(USER_DB, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 保存
# =========================
def save_users(data):
    os.makedirs("data", exist_ok=True)

    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================
# プラン取得
# =========================
def get_user_plan(user_id: str):
    users = load_users()
    return users.get(user_id, {}).get("plan", "free")


# =========================
# プラン更新
# =========================
def set_user_plan(user_id: str, plan: str):
    users = load_users()

    if user_id not in users:
        users[user_id] = {}

    users[user_id]["plan"] = plan

    save_users(users)