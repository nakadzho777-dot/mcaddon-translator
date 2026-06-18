import time
from datetime import datetime, timedelta

from core.logger import log_event
from core.plan_manager import get_user_plan


# =========================
# シンプルレート制限
# =========================
REQUEST_LOG = {}


def rate_limit(user_id: str, limit: int = 60, window_sec: int = 60):
    now = time.time()

    if user_id not in REQUEST_LOG:
        REQUEST_LOG[user_id] = []

    REQUEST_LOG[user_id] = [
        t for t in REQUEST_LOG[user_id]
        if now - t < window_sec
    ]

    if len(REQUEST_LOG[user_id]) >= limit:
        log_event(f"RATE_LIMIT_BLOCK {user_id}", level="WARNING")
        return False

    REQUEST_LOG[user_id].append(now)
    return True


# =========================
# 権限チェック
# =========================
def has_permission(user_id: str, action: str):
    plan = get_user_plan(user_id)

    permissions = {
        "free": ["read", "generate_article"],
        "pro": ["read", "generate_article", "seo", "rewrite"],
        "business": ["all"]
    }

    allowed = permissions.get(plan, [])

    if "all" in allowed:
        return True

    return action in allowed


# =========================
# セキュア実行ラッパー
# =========================
def secure_execute(user_id: str, action: str, func, *args, **kwargs):
    if not rate_limit(user_id):
        return {"error": "RATE_LIMIT"}

    if not has_permission(user_id, action):
        log_event(f"PERMISSION_DENIED {user_id} {action}", level="WARNING")
        return {"error": "NO_PERMISSION"}

    try:
        result = func(*args, **kwargs)

        log_event(f"ACTION_OK {user_id} {action}")

        return result

    except Exception as e:
        log_event(f"ACTION_ERROR {user_id} {action} {e}", level="ERROR")

        return {"error": "EXECUTION_FAILED"}


# =========================
# セッション検証（簡易）
# =========================
def validate_session(user_id: str, token: str):
    if not token or len(token) < 10:
        return False

    # 本番ではJWTなどに置き換え
    return True