import os
import json
import shutil
from datetime import datetime

from core.logger import log_event

BACKUP_DIR = "data/backups"


# =========================
# 安全書き込み（原子操作）
# =========================
def safe_write(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    temp_path = path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.replace(temp_path, path)

    log_event(f"SAFE_WRITE {path}")


# =========================
# バックアップ作成
# =========================
def create_backup(file_path: str):
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if not os.path.exists(file_path):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(
        BACKUP_DIR,
        f"{os.path.basename(file_path)}_{timestamp}.bak"
    )

    shutil.copy2(file_path, backup_path)

    log_event(f"BACKUP_CREATED {backup_path}")

    return backup_path


# =========================
# ロールバック
# =========================
def rollback_latest(file_name: str):
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if file_name in f],
        reverse=True
    )

    if not backups:
        return None

    latest = backups[0]
    backup_path = os.path.join(BACKUP_DIR, latest)

    target_path = os.path.join("data", file_name)

    shutil.copy2(backup_path, target_path)

    log_event(f"ROLLBACK {file_name}")

    return target_path


# =========================
# データ検証
# =========================
def validate_data(data: dict, required_keys: list):
    for key in required_keys:
        if key not in data:
            return False

    return True


# =========================
# 安全ロード
# =========================
def safe_load(path: str):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)