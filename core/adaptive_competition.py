from core.logger import log_event
from core.growth_engine import growth_score
from core.ops_dashboard import get_dashboard


# =========================
# 競合状況ダミー（本来は外部API）
# =========================
def competitor_snapshot():
    return {
        "feature_parity": 0.7,
        "price_pressure": 0.6,
        "market_saturation": 0.5
    }


# =========================
# 市場適応スコア
# =========================
def market_fit_score():
    growth = growth_score()
    comp = competitor_snapshot()

    score = 0

    score += growth * 0.6
    score += (1 - comp["market_saturation"]) * 20

    return min(score, 100)


# =========================
# 改善アクション決定
# =========================
def adaptation_actions():
    comp = competitor_snapshot()
    score = market_fit_score()

    actions = []

    if comp["feature_parity"] > 0.6:
        actions.append("INNOVATE_FEATURES")

    if comp["price_pressure"] > 0.5:
        actions.append("OPTIMIZE_PRICING")

    if score < 50:
        actions.append("REPOSITION_PRODUCT")

    if score >= 80:
        actions.append("SCALE_MARKETING")

    return actions


# =========================
# 競争診断
# =========================
def competition_diagnosis():
    score = market_fit_score()
    actions = adaptation_actions()

    log_event(f"COMPETITION_DIAGNOSIS {score}")

    return {
        "market_fit_score": score,
        "actions": actions
    }


# =========================
# 自動適応ループ
# =========================
def run_adaptive_loop():
    return competition_diagnosis()