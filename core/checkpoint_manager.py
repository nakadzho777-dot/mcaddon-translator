import os
import json
from datetime import datetime

from core.logger import log_event

CHECKPOINT_DIR = "data/checkpoints"


# =========================
# 保存
# =========================
def save_checkpoint(name: str, data: dict):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    path = os.path.join(CHECKPOINT_DIR, f"{name}.json")

    payload = {
        "saved_at": datetime.now().isoformat(),
        "data": data
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    log_event(f"CHECKPOINT_SAVE {name}")


# =========================
# 読み込み
# =========================
def load_checkpoint(name: str):
    path = os.path.join(CHECKPOINT_DIR, f"{name}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 削除
# =========================
def delete_checkpoint(name: str):
    path = os.path.join(CHECKPOINT_DIR, f"{name}.json")

    if os.path.exists(path):
        os.remove(path)
        log_event(f"CHECKPOINT_DELETE {name}")


# =========================
# 自動復元
# =========================
def restore_latest():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    files = os.listdir(CHECKPOINT_DIR)

    if not files:
        return None

    latest_file = max(
        files,
        key=lambda x: os.path.getmtime(os.path.join(CHECKPOINT_DIR, x))
    )

    path = os.path.join(CHECKPOINT_DIR, latest_file)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    log_event(f"CHECKPOINT_RESTORE {latest_file}")

    return data