import json
import os
from datetime import datetime

from core.logger import log_event
from core.plan_manager import get_all_users  # 想定：全ユーザー取得関数


# =========================
# 収益集計
# =========================
def calculate_revenue():
    users = get_all_users()

    revenue = {
        "free": 0,
        "pro": 0,
        "business": 0
    }

    pricing = {
        "pro": 980,
        "business": 2980
    }

    for user in users:
        plan = user.get("plan", "free")

        if plan in pricing:
            revenue[plan] += pricing[plan]

    total = sum(revenue.values())

    return {
        "breakdown": revenue,
        "total": total
    }


# =========================
# 利用状況分析
# =========================
def analyze_usage():
    users = get_all_users()

    stats = {
        "total_users": len(users),
        "free_users": 0,
        "pro_users": 0,
        "business_users": 0
    }

    for user in users:
        plan = user.get("plan", "free")

        if plan == "free":
            stats["free_users"] += 1
        elif plan == "pro":
            stats["pro_users"] += 1
        elif plan == "business":
            stats["business_users"] += 1

    return stats


# =========================
# ダッシュボード生成
# =========================
def generate_dashboard():
    revenue = calculate_revenue()
    usage = analyze_usage()

    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "revenue": revenue,
        "usage": usage,
        "status": "active"
    }

    os.makedirs("logs", exist_ok=True)

    with open("logs/dashboard.json", "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    log_event("BI_DASHBOARD_UPDATED")

    return dashboard


# =========================
# KPIチェック
# =========================
def get_kpi():
    data = generate_dashboard()

    return {
        "MRR": data["revenue"]["total"],
        "users": data["usage"]["total_users"],
        "conversion": (
            data["usage"]["pro_users"] /
            max(data["usage"]["total_users"], 1)
        )
    }