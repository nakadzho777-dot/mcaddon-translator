from datetime import datetime

from core.analytics_engine import get_analytics_report
from core.control_panel import get_system_status
from core.audit_engine import get_user_history
from core.validation_engine import system_health_score
from core.logger import log_event


# =========================
# ダッシュボード生成
# =========================
def build_unified_dashboard(user_id: str, validation_results: dict):
    log_event("DASHBOARD_RENDER")

    system_status = get_system_status()
    analytics = get_analytics_report()
    user_history = get_user_history(user_id)

    health = system_health_score(validation_results)

    return {
        "timestamp": datetime.now().isoformat(),

        # システム状態
        "system": system_status,

        # 分析
        "analytics": analytics,

        # ユーザー履歴
        "user_activity": {
            "recent_actions": user_history[-10:],
            "total_actions": len(user_history)
        },

        # 健全性
        "health_score": health,
        "status": "OK" if health > 80 else "WARNING" if health > 50 else "CRITICAL"
    }


# =========================
# サマリー表示（軽量版）
# =========================
def get_dashboard_summary(user_id: str):
    log_event("DASHBOARD_SUMMARY")

    analytics = get_analytics_report()

    return {
        "revenue_estimate": analytics.get("revenue", 0),
        "top_features": analytics.get("top_features", []),
        "conversion_rate": analytics.get("conversion_rate", 0),
        "generated_at": datetime.now().isoformat()
    }


# =========================
# リアルタイム監視データ
# =========================
def get_realtime_view():
    return {
        "status": "LIVE",
        "time": datetime.now().isoformat(),
        "metrics": {
            "cpu": 0.0,
            "memory": 0.0,
            "requests": 0
        }
    }