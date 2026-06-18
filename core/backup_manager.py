import os
import shutil
from datetime import datetime

from core.logger import log_event


BACKUP_DIR = "backups"


# =========================
# フルバックアップ作成
# =========================
def create_backup(target_paths: list):
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, timestamp)

    os.makedirs(backup_path, exist_ok=True)

    for path in target_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.copytree(path, os.path.join(backup_path, os.path.basename(path)))
            else:
                shutil.copy2(path, backup_path)

    log_event(f"BACKUP_CREATED {timestamp}")

    return backup_path


# =========================
# バックアップ一覧
# =========================
def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return []

    return sorted(os.listdir(BACKUP_DIR), reverse=True)


# =========================
# 復元処理
# =========================
def restore_backup(backup_name: str, restore_path: str):
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    if not os.path.exists(backup_path):
        log_event(f"RESTORE_FAILED {backup_name}", level="ERROR")
        return False

    for item in os.listdir(backup_path):
        src = os.path.join(backup_path, item)
        dst = os.path.join(restore_path, item)

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    log_event(f"RESTORE_SUCCESS {backup_name}")

    return True


# =========================
# 自動バックアップ（軽量）
# =========================
def auto_backup(paths: list, interval_sec: int = 3600):
    import threading
    import time

    def loop():
        while True:
            create_backup(paths)
            time.sleep(interval_sec)

    t = threading.Thread(target=loop, daemon=True)
    t.start()

    log_event("AUTO_BACKUP_STARTED")