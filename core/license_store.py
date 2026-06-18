import os
import json
import secrets
from datetime import datetime

LICENSE_DB = "data/licenses.json"


def ensure_db():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(LICENSE_DB):
        with open(LICENSE_DB, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def load_db():
    ensure_db()

    with open(LICENSE_DB, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    ensure_db()

    with open(LICENSE_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_license_key():
    return "MCA-PRO-" + secrets.token_hex(12).upper()


def create_license(email: str, source: str = "stripe"):
    data = load_db()

    for key, value in data.items():
        if value.get("email") == email and value.get("status") == "active":
            return key

    key = generate_license_key()

    data[key] = {
        "email": email,
        "plan": "pro",
        "status": "active",
        "source": source,
        "created_at": datetime.now().isoformat(),
    }

    save_db(data)
    return key


def verify_license(key: str):
    data = load_db()
    item = data.get(key)

    if not item:
        return {"valid": False}

    return {
        "valid": item.get("status") == "active",
        "plan": item.get("plan"),
        "email": item.get("email"),
    }