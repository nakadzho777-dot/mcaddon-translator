import json
import os
from datetime import datetime

PLAN_FILE = "data/plans.json"


# =========================
# 初期化
# =========================
def init_plans():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(PLAN_FILE):
        with open(PLAN_FILE, "w") as f:
            json.dump({}, f)


# =========================
# ユーザープラン取得
# =========================
def get_plan(user: str):

    with open(PLAN_FILE, "r") as f:
        data = json.load(f)

    return data.get(user, "FREE")


# =========================
# プラン設定
# =========================
def set_plan(user: str, plan: str):

    with open(PLAN_FILE, "r") as f:
        data = json.load(f)

    data[user] = plan

    with open(PLAN_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# 制限チェック
# =========================
def is_allowed(user: str, action: str, count: int):

    plan = get_plan(user)

    if plan == "PRO":
        return True

    # FREE制限
    if action == "export":
        return count < 5

    if action == "project":
        return count < 3

    return True