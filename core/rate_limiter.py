import time
from collections import defaultdict

from core.logger import log_event


# =========================
# メモリベース制限ストア
# =========================
request_log = defaultdict(list)


# =========================
# レート制限チェック
# =========================
def is_allowed(user_id: str, limit: int = 10, window_sec: int = 60):
    now = time.time()

    # 古いログ削除
    request_log[user_id] = [
        t for t in request_log[user_id]
        if now - t < window_sec
    ]

    if len(request_log[user_id]) >= limit:
        log_event(f"RATE_LIMIT {user_id}", level="WARNING")
        return False

    request_log[user_id].append(now)

    return True


# =========================
# APIガード
# =========================
def rate_limit_guard(user_id: str, limit: int = 10, window_sec: int = 60):
    if not is_allowed(user_id, limit, window_sec):
        return {
            "status": "blocked",
            "reason": "rate_limit_exceeded"
        }

    return {"status": "ok"}


# =========================
# バースト検知
# =========================
def detect_burst(user_id: str):
    now = time.time()

    recent = [t for t in request_log[user_id] if now - t < 5]

    if len(recent) > 5:
        log_event(f"BURST_DETECTED {user_id}", level="WARNING")
        return True

    return False