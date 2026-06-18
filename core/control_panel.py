import json
from datetime import datetime

from core.business_intelligence import generate_dashboard
from core.analytics_engine import get_analytics_report
from core.validation_engine import system_health_score
from core.config_center import load_config
from core.logger import log_event


# =========================
# システム状態取得
# =========================
def get_system_status():
    dashboard = generate_dashboard()
    analytics = get_analytics_report()

    return {
        "time": datetime.now().isoformat(),
        "revenue": dashboard.get("revenue"),
        "users": dashboard.get("usage"),
        "analytics": analytics,
        "config": load_config()
    }


# =========================
# 健全性チェック
# =========================
def get_health_summary(validation_results: dict):
    score = system_health_score(validation_results)

    return {
        "health_score": score,
        "status": "OK" if score > 80 else "WARNING" if score > 50 else "CRITICAL"
    }


# =========================
# 操作コマンド
# =========================
def execute_command(command: str):
    log_event(f"CONTROL_COMMAND {command}")

    commands = {
        "restart": lambda: "SYSTEM_RESTART_TRIGGERED",
        "snapshot": lambda: "SYSTEM_SNAPSHOT_CREATED",
        "health": lambda: get_system_status(),
    }

    func = commands.get(command)

    if not func:
        return {"error": "UNKNOWN_COMMAND"}

    return func()


# =========================
# ダッシュボードデータ生成
# =========================
def render_dashboard():
    status = get_system_status()

    return {
        "dashboard": status,
        "generated_at": datetime.now().isoformat()
    }