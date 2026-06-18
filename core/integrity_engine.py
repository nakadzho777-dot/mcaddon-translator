import json
import os

from core.logger import log_event


# =========================
# JSON安全読み込み
# =========================
def safe_load_json(path: str, default=None):
    if default is None:
        default = {}

    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        log_event(f"DATA_CORRUPTED {path} {e}", level="ERROR")
        return default


# =========================
# JSON安全書き込み
# =========================
def safe_write_json(path: str, data: dict):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        log_event(f"DATA_WRITTEN {path}")

    except Exception as e:
        log_event(f"WRITE_FAILED {path} {e}", level="ERROR")


# =========================
# 整合性チェック
# =========================
def validate_structure(data: dict, required_keys: list):
    missing = [k for k in required_keys if k not in data]

    if missing:
        log_event(f"STRUCTURE_MISSING {missing}", level="WARNING")

    return {
        "valid": len(missing) == 0,
        "missing": missing
    }


# =========================
# 自動修復
# =========================
def repair_data(data: dict, schema: dict):
    repaired = data.copy()

    for key, default_value in schema.items():
        if key not in repaired:
            repaired[key] = default_value
            log_event(f"AUTO_REPAIR_FIELD {key}")

    return repaired


# =========================
# 全体スキャン
# =========================
def scan_and_repair(file_map: dict):
    """
    file_map例:
    {
        "data/users.json": {"users": []},
        "data/logs.json": {"logs": []}
    }
    """

    results = {}

    for path, schema in file_map.items():
        data = safe_load_json(path)

        repaired = repair_data(data, schema)

        safe_write_json(path, repaired)

        results[path] = "OK"

    return results