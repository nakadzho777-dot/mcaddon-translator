from core.logger import log_event

from core.saas_core import run_full_cycle
from core.optimization_ai import generate_optimization_plan
from core.seo_growth_engine import build_growth_report
from core.revenue_dashboard import build_dashboard
from core.runtime_guard import monitored_run
from core.checkpoint_manager import save_checkpoint, restore_latest
from core.observability_manager import health_check


# =========================
# フル運用実行
# =========================
def run_full_operations():
    log_event("OPS_FULL_START")

    monitored_run("SEO", build_growth_report)
    monitored_run("OPTIMIZATION", generate_optimization_plan)
    monitored_run("REVENUE", build_dashboard)

    log_event("OPS_FULL_DONE")


# =========================
# 緊急復旧
# =========================
def emergency_recover():
    log_event("OPS_RECOVERY_TRIGGER")

    state = restore_latest()

    if state:
        log_event("OPS_STATE_RESTORED")
        return state

    log_event("OPS_NO_STATE_FOUND")
    return None


# =========================
# システムヘルスチェック
# =========================
def system_health():
    checks = {
        "seo": build_growth_report,
        "optimization": generate_optimization_plan,
        "revenue": build_dashboard
    }

    return health_check(checks)


# =========================
# スナップショット保存
# =========================
def snapshot_system():
    data = {
        "status": "snapshot",
        "components": [
            "seo",
            "optimization",
            "revenue"
        ]
    }

    save_checkpoint("ops_snapshot", data)

    log_event("OPS_SNAPSHOT_CREATED")

    return data