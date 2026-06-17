import json
import os
from datetime import datetime

UPDATE_FILE = "data/update.json"


# =========================
# 初期化
# =========================
def init_update():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(UPDATE_FILE):
        with open(UPDATE_FILE, "w") as f:
            json.dump({
                "version": "1.0.0",
                "message": "initial release",
                "download_url": "",
                "force_update": False,
                "updated_at": datetime.utcnow().isoformat()
            }, f, indent=2)


# =========================
# 最新情報取得
# =========================
def get_latest_version():

    with open(UPDATE_FILE, "r") as f:
        return json.load(f)


# =========================
# バージョン更新（管理用）
# =========================
def set_new_version(version: str, message: str, url: str, force: bool = False):

    data = {
        "version": version,
        "message": message,
        "download_url": url,
        "force_update": force,
        "updated_at": datetime.utcnow().isoformat()
    }

    with open(UPDATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return data