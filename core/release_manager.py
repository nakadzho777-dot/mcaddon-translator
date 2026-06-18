import json
import os
from datetime import datetime

from core.logger import log_event


RELEASE_FILE = "data/release.json"


# =========================
# 現在バージョン取得
# =========================
def get_current_version():
    if not os.path.exists(RELEASE_FILE):
        return "0.0.0"

    try:
        with open(RELEASE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except:
        return "0.0.0"


# =========================
# バージョン更新
# =========================
def set_version(version: str):
    os.makedirs("data", exist_ok=True)

    data = {
        "version": version,
        "updated_at": datetime.now().isoformat()
    }

    with open(RELEASE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log_event(f"VERSION_UPDATED {version}")


# =========================
# 安全アップデート判定
# =========================
def can_update(current: str, new: str):
    return new > current


# =========================
# ロールバック
# =========================
def rollback(previous_version: str):
    set_version(previous_version)
    log_event(f"ROLLBACK {previous_version}")


# =========================
# カナリアリリース（段階公開）
# =========================
def canary_release(version: str, user_id: str):
    # シンプルな分散（偶数IDだけ新バージョン）
    return int(user_id[-1]) % 2 == 0


# =========================
# リリース適用
# =========================
def apply_release(new_version: str, previous_version: str = None):
    current = get_current_version()

    if not can_update(current, new_version):
        return {"status": "blocked"}

    try:
        set_version(new_version)
        log_event(f"RELEASE_APPLIED {new_version}")

        return {"status": "success"}

    except Exception as e:
        log_event(f"RELEASE_FAILED {e}", level="ERROR")

        if previous_version:
            rollback(previous_version)

        return {"status": "rollback"}