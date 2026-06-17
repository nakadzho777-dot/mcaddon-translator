import json
import os
from core.auth import hash_password, verify_password

DB_FILE = "data/users.json"


# =========================
# 初期化
# =========================
def init_db():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)


# =========================
# ユーザー取得
# =========================
def load_users():

    with open(DB_FILE, "r") as f:
        return json.load(f)


# =========================
# 保存
# =========================
def save_users(data):

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# 登録
# =========================
def create_user(username, password):

    users = load_users()

    if username in users:
        return False

    users[username] = {
        "password": hash_password(password)
    }

    save_users(users)

    return True


# =========================
# 認証
# =========================
def authenticate(username, password):

    users = load_users()

    if username not in users:
        return False

    return verify_password(password, users[username]["password"])