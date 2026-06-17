import json
import os
import uuid
from datetime import datetime

USER_FILE = "data/users.json"


# =========================
# 初期化
# =========================
def init_users():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump({}, f)


# =========================
# ユーザー作成
# =========================
def create_user(username: str, password: str):

    with open(USER_FILE, "r") as f:
        users = json.load(f)

    if username in users:
        return None

    users[username] = {
        "password": password,
        "plan": "FREE",
        "created_at": datetime.utcnow().isoformat(),
        "token": None
    }

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

    return username


# =========================
# ログイン
# =========================
def login_user(username: str, password: str):

    with open(USER_FILE, "r") as f:
        users = json.load(f)

    user = users.get(username)

    if not user:
        return None

    if user["password"] != password:
        return None

    token = str(uuid.uuid4())
    user["token"] = token

    users[username] = user

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

    return token


# =========================
# トークン認証
# =========================
def get_user_by_token(token: str):

    with open(USER_FILE, "r") as f:
        users = json.load(f)

    for username, data in users.items():
        if data.get("token") == token:
            return username

    return None