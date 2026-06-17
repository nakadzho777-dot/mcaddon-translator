import json
import uuid
from datetime import datetime, timedelta


FILE = "licenses.json"


def load():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# ライセンス生成
# ----------------------------

def generate_license(user="user", days=30):

    data = load()

    key = str(uuid.uuid4()).upper()[:12]

    expire = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    data[key] = {
        "active": True,
        "user": user,
        "expire": expire
    }

    save(data)

    print("NEW LICENSE:", key)
    return key


# ----------------------------
# 無効化
# ----------------------------

def disable_license(key):

    data = load()

    if key in data:
        data[key]["active"] = False
        save(data)
        print("DISABLED:", key)
    else:
        print("NOT FOUND")


# ----------------------------
# 一覧表示
# ----------------------------

def list_licenses():

    data = load()

    for k, v in data.items():
        print(k, v)


# ----------------------------
# CLI操作
# ----------------------------

if __name__ == "__main__":

    while True:

        print("\n1: generate\n2: list\n3: disable\n0: exit")
        cmd = input("> ")

        if cmd == "1":
            user = input("user: ")
            days = int(input("days: "))
            generate_license(user, days)

        elif cmd == "2":
            list_licenses()

        elif cmd == "3":
            key = input("key: ")
            disable_license(key)

        elif cmd == "0":
            break