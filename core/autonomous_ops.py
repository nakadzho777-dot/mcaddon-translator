from core.logger import log_event
from core.ops_dashboard import get_dashboard, is_critical
from core.scaling_manager import trigger_scale_up
from core.backup_manager import create_backup


# =========================
# 障害分類
# =========================
def classify_issue(dashboard: dict):
    issues = []

    if dashboard["health_score"] < 50:
        issues.append("SYSTEM_DEGRADED")

    if dashboard["cost"] > 200:
        issues.append("COST_SPIKE")

    if len(dashboard["alerts"]) > 5:
        issues.append("ALERT_OVERLOAD")

    return issues


# =========================
# 自動復旧
# =========================
def auto_recover(issue: str):
    if issue == "SYSTEM_DEGRADED":
        create_backup(["core", "data"])
        log_event("AUTO_RECOVERY_BACKUP")

    if issue == "COST_SPIKE":
        trigger_scale_up()
        log_event("AUTO_RECOVERY_SCALE")

    if issue == "ALERT_OVERLOAD":
        log_event("AUTO_RECOVERY_ALERT_RESET")

    return True


# =========================
# 優先度判定
# =========================
def priority(issue: str):
    if issue == "SYSTEM_DEGRADED":
        return "CRITICAL"
    if issue == "COST_SPIKE":
        return "HIGH"
    return "MEDIUM"


# =========================
# オペレーションループ
# =========================
def run_ops_cycle():
    dashboard = get_dashboard()

    issues = classify_issue(dashboard)

    if not issues:
        return {
            "status": "ok",
            "message": "system healthy"
        }

    for issue in issues:
        log_event(f"OPS_ISSUE {issue} {priority(issue)}")
        auto_recover(issue)

    return {
        "status": "recovered",
        "issues": issues
    }


# =========================
# 緊急判定
# =========================
def emergency_mode():
    return is_critical()