from core.logger import log_event
from core.ops_dashboard import get_dashboard
from core.analytics_engine import track_event


# =========================
# ローンチ準備チェック
# =========================
def pre_launch_check():
    dashboard = get_dashboard()

    checks = {
        "health_ok": dashboard["health_score"] > 70,
        "cost_ok": dashboard["cost"] < 100,
        "no_critical_alerts": len(dashboard["alerts"]) < 3,
        "system_stable": True
    }

    return checks


# =========================
# ローンチ実行
# =========================
def launch_product():
    checks = pre_launch_check()

    if not all(checks.values()):
        log_event("LAUNCH_BLOCKED", level="ERROR")
        return {
            "status": "blocked",
            "checks": checks
        }

    log_event("PRODUCT_LAUNCH_SUCCESS")

    return {
        "status": "live",
        "message": "Product is now publicly available"
    }


# =========================
# 初期ユーザー計測
# =========================
def register_first_users(user_id: str):
    track_event(user_id, "launch_visit")

    log_event(f"NEW_USER {user_id}")

    return {
        "status": "tracked"
    }


# =========================
# ランディング状態取得
# =========================
def get_launch_status():
    dashboard = get_dashboard()

    return {
        "status": "live" if dashboard["health_score"] > 70 else "degraded",
        "health_score": dashboard["health_score"],
        "users": dashboard["analytics"]["active_users_7d"]
    }