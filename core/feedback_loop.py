from core.analytics_engine import get_analytics_report
from core.logger import log_event


# =========================
# 改善判断エンジン
# =========================
def analyze_system():
    report = get_analytics_report()

    insights = []

    # ユーザーが少ない
    if report["active_users_7d"] < 100:
        insights.append("USER_GROWTH_WEAK")

    # CVRが低い
    if report["conversion_rate"] < 0.05:
        insights.append("LOW_CONVERSION")

    # 成長スコアが低い
    if report["growth_score"] < 50:
        insights.append("WEAK_GROWTH")

    return insights


# =========================
# 改善アクション生成
# =========================
def generate_actions(insights: list):
    actions = []

    for i in insights:

        if i == "USER_GROWTH_WEAK":
            actions.append({
                "action": "SEO_BOOST",
                "priority": "HIGH",
                "message": "ブログ記事・SEO流入を増やす"
            })

        if i == "LOW_CONVERSION":
            actions.append({
                "action": "IMPROVE_LP",
                "priority": "HIGH",
                "message": "LP改善・CTA最適化"
            })

        if i == "WEAK_GROWTH":
            actions.append({
                "action": "PRODUCT_IMPROVE",
                "priority": "MEDIUM",
                "message": "機能UX改善・オンボーディング最適化"
            })

    return actions


# =========================
# 自動レポート
# =========================
def run_feedback_loop():
    insights = analyze_system()
    actions = generate_actions(insights)

    log_event(f"FEEDBACK_LOOP {len(actions)} actions generated")

    return {
        "insights": insights,
        "actions": actions
    }