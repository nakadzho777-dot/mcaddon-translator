from core.analytics_engine import get_analytics_report
from core.cost_manager import get_total_cost, calculate_profit
from core.audit_logger import audit_report
from core.alert_engine import get_recent_alerts
from core.feedback_loop import run_feedback_loop


# =========================
# システムヘルススコア
# =========================
def system_health():
    analytics = get_analytics_report()
    cost = get_total_cost()
    audit = audit_report()
    alerts = get_recent_alerts()

    score = 100

    # ユーザー不足
    if analytics["active_users_7d"] < 100:
        score -= 20

    # コスト過多
    if cost > 100:
        score -= 20

    # アラート多い
    if len(alerts) > 5:
        score -= 20

    # 監査異常
    if audit["sensitive_actions"] > 10:
        score -= 10

    return max(score, 0)


# =========================
# 統合ダッシュボード
# =========================
def get_dashboard():
    analytics = get_analytics_report()
    cost = get_total_cost()
    profit = calculate_profit(revenue=analytics["active_users_7d"] * 1.5)

    alerts = get_recent_alerts()
    audit = audit_report()
    feedback = run_feedback_loop()

    return {
        "analytics": analytics,
        "cost": cost,
        "profit": profit,
        "alerts": alerts,
        "audit": audit,
        "feedback": feedback,
        "health_score": system_health()
    }


# =========================
# 緊急状態判定
# =========================
def is_critical():
    return system_health() < 50