from core.logger import log_event
from core.cost_manager import record_cost


# =========================
# プラン定義
# =========================
PLANS = {
    "free": {
        "price": 0,
        "api_limit": 50,
        "features": ["basic"]
    },
    "pro": {
        "price": 9.99,
        "api_limit": 1000,
        "features": ["basic", "analytics", "automation"]
    },
    "enterprise": {
        "price": 49.99,
        "api_limit": 10000,
        "features": ["all"]
    }
}


# =========================
# ユーザープラン取得
# =========================
USER_PLANS = {}


def get_user_plan(user_id: str):
    return USER_PLANS.get(user_id, "free")


# =========================
# プラン変更
# =========================
def set_user_plan(user_id: str, plan: str):
    if plan not in PLANS:
        return {"status": "error", "message": "invalid plan"}

    USER_PLANS[user_id] = plan

    log_event(f"PLAN_CHANGED {user_id} {plan}")

    return {"status": "ok"}


# =========================
# API利用チェック
# =========================
USAGE_COUNTER = {}


def check_api_usage(user_id: str):
    plan = get_user_plan(user_id)
    limit = PLANS[plan]["api_limit"]

    usage = USAGE_COUNTER.get(user_id, 0)

    if usage >= limit:
        log_event(f"API_LIMIT_EXCEEDED {user_id}")
        return False

    USAGE_COUNTER[user_id] = usage + 1
    return True


# =========================
# 課金シミュレーション
# =========================
def calculate_revenue():
    revenue = 0

    for user_id, plan in USER_PLANS.items():
        revenue += PLANS[plan]["price"]

    return revenue


# =========================
# 利益計算
# =========================
def calculate_profit(total_cost: float):
    revenue = calculate_revenue()

    profit = revenue - total_cost

    log_event(f"PROFIT_CALCULATED {profit}")

    return profit


# =========================
# 収益最適化アドバイス
# =========================
def optimize_pricing():
    revenue = calculate_revenue()

    if revenue < 100:
        return {
            "action": "UPSELL_PRO",
            "message": "FreeユーザーをProへ誘導"
        }

    if revenue > 1000:
        return {
            "action": "ENTERPRISE_EXPANSION",
            "message": "法人プラン強化"
        }

    return {
        "action": "STABLE",
        "message": "現状維持"
    }