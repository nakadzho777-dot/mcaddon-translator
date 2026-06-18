import time
import traceback

from core.logger import log_event
from core.alert_engine import trigger_alert


# =========================
# 安全実行ラッパー
# =========================
def safe_run(name: str, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)

    except Exception as e:
        error_trace = traceback.format_exc()

        log_event(f"HEAL_ERROR {name} {e}", level="ERROR")

        trigger_alert(
            "WARNING",
            f"Auto recovery triggered: {name}",
            {"error": str(e)}
        )

        # 自動リトライ
        return retry(name, func, *args, **kwargs)


# =========================
# リトライ機構
# =========================
def retry(name: str, func, *args, retries: int = 2, **kwargs):
    for attempt in range(retries):
        try:
            log_event(f"RETRY {name} attempt={attempt+1}")

            time.sleep(1)

            return func(*args, **kwargs)

        except Exception as e:
            log_event(f"RETRY_FAIL {name} {e}", level="WARNING")

    trigger_alert(
        "CRITICAL",
        f"Permanent failure: {name}"
    )

    return {"error": "MAX_RETRIES_EXCEEDED"}


# =========================
# プロセス自己回復
# =========================
def recover_system_component(component_name: str, restart_func):
    try:
        log_event(f"RECOVERY_START {component_name}")

        restart_func()

        log_event(f"RECOVERY_SUCCESS {component_name}")

        return True

    except Exception as e:
        log_event(f"RECOVERY_FAILED {component_name} {e}", level="CRITICAL")

        trigger_alert("FATAL", f"Component failure: {component_name}")

        return False


# =========================
# ヘルスチェック自動修復
# =========================
def auto_heal(metrics: dict):
    if metrics.get("error_rate", 0) > 0.3:
        trigger_alert("WARNING", "High error rate - healing triggered")

    if metrics.get("memory", 0) > 85:
        trigger_alert("WARNING", "Memory pressure detected")

    if metrics.get("cpu", 0) > 90:
        trigger_alert("WARNING", "CPU overload detected")