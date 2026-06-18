import json
import os
from datetime import datetime

from core.logger import log_event
from core.alert_engine import trigger_alert


# =========================
# JSON検証
# =========================
def validate_json(file_path: str):
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)

        return True

    except Exception as e:
        log_event(f"DATA_CORRUPT {file_path} {e}", level="ERROR")

        trigger_alert(
            "WARNING",
            "Data corruption detected",
            {"file": file_path, "error": str(e)}
        )

        return False


# =========================
# 自動修復（バックアップ復元）
# =========================
def auto_repair(file_path: str, backup_path: str):
    try:
        if not os.path.exists(backup_path):
            trigger_alert("CRITICAL", "No backup available for recovery")
            return False

        with open(backup_path, "r", encoding="utf-8") as f:
            backup_data = f.read()

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(backup_data)

        log_event(f"DATA_REPAIR_SUCCESS {file_path}")

        return True

    except Exception as e:
        log_event(f"DATA_REPAIR_FAIL {e}", level="CRITICAL")

        trigger_alert("FATAL", "Data recovery failed")

        return False


# =========================
# データ整合性チェック（複数ファイル）
# =========================
def check_system_integrity(file_list: list):
    results = {}

    for file_path in file_list:
        results[file_path] = validate_json(file_path)

    return results


# =========================
# 整合性スコア
# =========================
def integrity_score(results: dict):
    if not results:
        return 100

    ok = len([v for v in results.values() if v])

    return (ok / len(results)) * 100


# =========================
# 自動整合性監視
# =========================
def monitor_integrity(file_list: list, backup_map: dict):
    results = check_system_integrity(file_list)

    score = integrity_score(results)

    if score < 80:
        trigger_alert(
            "CRITICAL",
            "System integrity degraded",
            {"score": score}
        )

    # 壊れているものを自動修復
    for file_path, ok in results.items():
        if not ok and file_path in backup_map:
            auto_repair(file_path, backup_map[file_path])

    return {
        "score": score,
        "results": results
    }