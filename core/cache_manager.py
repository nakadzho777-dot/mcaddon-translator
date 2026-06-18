import time
import json
import os
import hashlib

from core.logger import log_event


CACHE_FILE = "data/cache.json"


# =========================
# キャッシュロード
# =========================
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# =========================
# キャッシュ保存
# =========================
def save_cache(cache):
    os.makedirs("data", exist_ok=True)

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# =========================
# キー生成
# =========================
def make_key(prefix: str, data: str):
    raw = f"{prefix}:{data}"
    return hashlib.md5(raw.encode()).hexdigest()


# =========================
# キャッシュ取得
# =========================
def get_cache(key: str):
    cache = load_cache()

    item = cache.get(key)

    if not item:
        return None

    # TTLチェック
    if time.time() > item["expire"]:
        del cache[key]
        save_cache(cache)
        return None

    log_event(f"CACHE_HIT {key}")

    return item["value"]


# =========================
# キャッシュ保存
# =========================
def set_cache(key: str, value, ttl: int = 300):
    cache = load_cache()

    cache[key] = {
        "value": value,
        "expire": time.time() + ttl
    }

    save_cache(cache)

    log_event(f"CACHE_SET {key}")


# =========================
# 高速ラッパー
# =========================
def cached(prefix: str, data: str, func, ttl: int = 300):
    key = make_key(prefix, data)

    cached_value = get_cache(key)

    if cached_value is not None:
        return cached_value

    result = func()

    set_cache(key, result, ttl)

    return result