import os
import psutil
from core.logger import log_event


# =========================
# CPU負荷チェック
# =========================
def get_cpu_load():
    return psutil.cpu_percent(interval=1)


# =========================
# メモリ負荷チェック
# =========================
def get_memory_load():
    return psutil.virtual_memory().percent


# =========================
# スケール判断
# =========================
def should_scale():
    cpu = get_cpu_load()
    mem = get_memory_load()

    if cpu > 80 or mem > 80:
        return True

    return False


# =========================
# スケールアクション
# =========================
def trigger_scale_up():
    log_event("SCALE_UP_TRIGGERED")

    return {
        "action": "scale_up",
        "message": "Increase instances or workers"
    }


# =========================
# ワーカー数調整
# =========================
def adjust_workers(current_workers: int):
    cpu = get_cpu_load()

    if cpu > 80:
        return current_workers + 2

    if cpu < 30 and current_workers > 1:
        return current_workers - 1

    return current_workers


# =========================
# スケール監視ループ
# =========================
def monitor_scaling(interval: int = 10):
    import time

    while True:
        if should_scale():
            trigger_scale_up()

        log_event("SCALING_CHECK")

        time.sleep(interval)