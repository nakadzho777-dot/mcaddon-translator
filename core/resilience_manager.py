import time
import random

from core.logger import log_event


# =========================
# フォールバック実行
# =========================
def with_fallback(primary_func, fallback_func, *args, **kwargs):
    try:
        return primary_func(*args, **kwargs)

    except Exception as e:
        log_event(f"PRIMARY_FAILED {primary_func.__name__} {e}", level="ERROR")

        return fallback_func(*args, **kwargs)


# =========================
# リトライ付き実行
# =========================
def with_retry(func, retries=3, delay=2, *args, **kwargs):
    for i in range(retries):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            log_event(f"RETRY {func.__name__} {i+1} {e}", level="ERROR")
            time.sleep(delay)

    raise Exception(f"FAILED_AFTER_RETRIES {func.__name__}")


# =========================
# キャッシュフォールバック
# =========================
CACHE = {}


def cached_or_fallback(key, primary_func, *args, **kwargs):
    if key in CACHE:
        return CACHE[key]

    try:
        result = primary_func(*args, **kwargs)
        CACHE[key] = result
        return result

    except Exception as e:
        log_event(f"CACHE_FALLBACK {key} {e}", level="ERROR")
        return CACHE.get(key, None)


# =========================
# ダミーモード（緊急用）
# =========================
def safe_mode_response():
    responses = [
        "現在軽量モードで動作中です",
        "一部機能を制限して稼働しています",
        "システムは復旧処理中です"
    ]

    return random.choice(responses)