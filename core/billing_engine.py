from core.logger import log_event
from core.plan_manager import get_user_plan


# =========================
# プラン定義
# =========================
PLAN_LIMITS = {
    "free": {
        "daily_requests": 20,
        "seo_generation": 0,
        "priority": "low"
    },
    "pro": {
        "daily_requests": 500,
        "seo_generation": 50,
        "priority": "high"
    },
    "enterprise": {
        "daily_requests": -1,  # 無制限
        "seo_generation": -1,
        "priority": "max"
    }
}


# =========================
# 利用制限チェック
# =========================
def check_limit(user_id: str, feature: str, usage: int):
    plan = get_user_plan(user_id)

    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

    limit = limits.get(feature, 0)

    if limit == -1:
        return True

    if usage >= limit:
        log_event(f"LIMIT_EXCEEDED {user_id} {feature}", level="WARNING")
        return False

    return True


# =========================
# 機能アクセス制御
# =========================
def allow_feature(user_id: str, feature: str):
    plan = get_user_plan(user_id)

    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

    if feature == "seo" and limits["seo_generation"] == 0:
        return False

    return True


# =========================
# 使用量記録（簡易）
# =========================
USER_USAGE = {}


def track_usage(user_id: str, feature: str):
    if user_id not in USER_USAGE:
        USER_USAGE[user_id] = {}

    if feature not in USER_USAGE[user_id]:
        USER_USAGE[user_id][feature] = 0

    USER_USAGE[user_id][feature] += 1

    log_event(f"USAGE {user_id} {feature} {USER_USAGE[user_id][feature]}")


# =========================
# アップグレード提案
# =========================
def suggest_plan_upgrade(user_id: str):
    plan = get_user_plan(user_id)

    if plan == "free":
        return {
            "upgrade": True,
            "message": "ProにするとSEO生成と高速翻訳が解放されます"
        }

    if plan == "pro":
        return {
            "upgrade": True,
            "message": "Enterpriseで完全無制限になります"
        }

    return {
        "upgrade": False,
        "message": "最上位プランです"
    }