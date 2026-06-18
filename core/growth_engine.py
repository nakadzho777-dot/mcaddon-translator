from core.logger import log_event
from core.analytics_engine import get_analytics_report
from core.monetization_engine import get_user_plan


# =========================
# ユーザー獲得戦略
# =========================
def acquisition_strategy():
    return {
        "seo": "blog + keyword pages",
        "social": "short-form content",
        "referral": "invite system"
    }


# =========================
# リテンション改善
# =========================
def retention_actions():
    return [
        "onboarding_optimization",
        "email_reminders",
        "feature_tips",
        "usage_recommendations"
    ]


# =========================
# バイラル係数計算
# =========================
def calculate_k_factor(invites: int, conversions: int):
    if invites == 0:
        return 0

    return conversions / invites


# =========================
# 成長スコア
# =========================
def growth_score():
    data = get_analytics_report()

    score = 0

    if data["active_users_7d"] > 100:
        score += 30

    if data["conversion_rate"] > 0.05:
        score += 30

    if data["retention_rate"] > 0.4:
        score += 40

    return score


# =========================
# 成長診断
# =========================
def growth_diagnosis():
    score = growth_score()

    if score < 50:
        action = "IMPROVE_ONBOARDING"
    elif score < 80:
        action = "BOOST_ACQUISITION"
    else:
        action = "SCALE_UP"

    log_event(f"GROWTH_DIAGNOSIS {score} {action}")

    return {
        "score": score,
        "action": action
    }


# =========================
# 成長ループ実行
# =========================
def run_growth_loop():
    diagnosis = growth_diagnosis()

    return {
        "strategy": acquisition_strategy(),
        "retention": retention_actions(),
        "diagnosis": diagnosis
    }