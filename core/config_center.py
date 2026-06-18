import json
import os
from datetime import datetime

from core.logger import log_event

CONFIG_PATH = "data/config.json"


# =========================
# デフォルト設定
# =========================
DEFAULT_CONFIG = {
    "env": "production",
    "features": {
        "seo_generator": True,
        "auto_translation": True,
        "auto_blog": True
    },
    "limits": {
        "max_workers": 3,
        "rate_limit": 100
    }
}


# =========================
# 読み込み
# =========================
def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        log_event(f"CONFIG_LOAD_ERROR {e}", level="ERROR")
        return DEFAULT_CONFIG


# =========================
# 書き込み
# =========================
def save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    log_event("CONFIG_UPDATED")


# =========================
# 値取得
# =========================
def get(key: str, default=None):
    config = load_config()

    keys = key.split(".")

    value = config

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default

    return value


# =========================
# 値更新
# =========================
def set_value(key: str, value):
    config = load_config()

    keys = key.split(".")

    target = config

    for k in keys[:-1]:
        target = target.setdefault(k, {})

    target[keys[-1]] = value

    save_config(config)

    log_event(f"CONFIG_SET {key}={value}")


# =========================
# フィーチャーフラグ制御
# =========================
def is_enabled(feature: str):
    return get(f"features.{feature}", False)


# =========================
# 環境切り替え
# =========================
def set_env(env: str):
    config = load_config()

    config["env"] = env

    save_config(config)

    log_event(f"ENV_CHANGED {env}")