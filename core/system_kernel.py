import traceback

from core.logger import log_event

from core.ops_center import run_full_operations
from core.observability_manager import system_health
from core.checkpoint_manager import restore_latest, save_checkpoint
from core.runtime_guard import monitored_run


# =========================
# 初期化
# =========================
def initialize_system():
    log_event("KERNEL_INIT_START")

    try:
        state = restore_latest()

        if state:
            log_event("KERNEL_STATE_RESTORED")

        else:
            log_event("KERNEL_FRESH_START")

        save_checkpoint("kernel_boot", {"status": "booted"})

        log_event("KERNEL_INIT_DONE")

    except Exception as e:
        log_event(f"KERNEL_INIT_FAIL {e}", level="ERROR")
        print(traceback.format_exc())


# =========================
# メインループ
# =========================
def run_system_cycle():
    log_event("KERNEL_CYCLE_START")

    monitored_run("OPS", run_full_operations)
    monitored_run("HEALTH", system_health)

    log_event("KERNEL_CYCLE_DONE")


# =========================
# 安全停止
# =========================
def shutdown_system():
    log_event("KERNEL_SHUTDOWN")

    save_checkpoint("shutdown", {"status": "stopped"})

    print("🛑 システム停止完了")


# =========================
# 完全起動
# =========================
def start_kernel():
    initialize_system()

    try:
        run_system_cycle()

    except Exception as e:
        log_event(f"KERNEL_CRASH {e}", level="ERROR")
        print("❌ 致命的エラー発生")

        restore_latest()