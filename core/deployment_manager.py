import json
import os
import shutil
from datetime import datetime

from core.logger import log_event

DEPLOY_DIR = "release"
VERSION_FILE = "data/version.json"


# =========================
# バージョン取得
# =========================
def get_version():
    if not os.path.exists(VERSION_FILE):
        return {"version": "0.0.0"}

    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# バージョン更新
# =========================
def update_version(new_version: str):
    os.makedirs("data", exist_ok=True)

    data = {
        "version": new_version,
        "updated_at": datetime.now().isoformat()
    }

    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log_event(f"VERSION_UPDATED {new_version}")


# =========================
# ビルド作成
# =========================
def build_release(source_dir=".", output_dir=DEPLOY_DIR):
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    build_path = os.path.join(output_dir, f"build_{timestamp}")

    shutil.copytree(source_dir, build_path, ignore=shutil.ignore_patterns(
        "build", "dist", "__pycache__", ".git"
    ))

    log_event(f"BUILD_CREATED {build_path}")

    return build_path


# =========================
# デプロイ実行
# =========================
def deploy(build_path: str):
    target = "production"

    if not os.path.exists(build_path):
        return {"error": "BUILD_NOT_FOUND"}

    shutil.copytree(build_path, target, dirs_exist_ok=True)

    update_version(datetime.now().strftime("%Y.%m.%d.%H%M"))

    log_event(f"DEPLOYED {build_path}")

    return {"status": "DEPLOYED", "target": target}


# =========================
# ロールバック
# =========================
def rollback(last_build: str):
    if not os.path.exists(last_build):
        return {"error": "NO_BUILD"}

    shutil.copytree(last_build, "production", dirs_exist_ok=True)

    log_event(f"ROLLBACK {last_build}")

    return {"status": "ROLLED_BACK"}