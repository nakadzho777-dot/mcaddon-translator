import os

from core.logger import log_event
from core.plan_manager import get_user_plan
from core.stripe_payments import create_checkout_session

from tools.auto_blog_generator import generate_article
from core.ranking_engine import generate_ranking
from core.rewrite_engine import run_rewrite
from core.seo_optimizer import generate_seo_report
from core.seo_growth_engine import build_growth_report
from core.ctr_optimizer import generate_ctr_titles
from core.internal_linker import run_internal_linking
from services.revenue_dashboard import build_dashboard


# =========================
# ユーザー実行ゲート
# =========================
def run_user_action(user_id: str, action: str, keyword: str = None):
    plan = get_user_plan(user_id)

    log_event(f"USER_ACTION {user_id} {action} {keyword}")

    # 無料制限
    if plan == "free" and action in ["generate", "rewrite", "seo"]:
        return "upgrade_required"

    # =========================
    # 記事生成
    # =========================
    if action == "generate":
        return generate_article(keyword)

    # =========================
    # 全体最適化
    # =========================
    if action == "optimize":
        generate_ranking()
        generate_ctr_titles()
        generate_seo_report()
        build_growth_report()
        run_rewrite()
        run_internal_linking()
        build_dashboard()

        return "optimization_complete"

    # =========================
    # 課金導線
    # =========================
    if action == "upgrade":
        return create_checkout_session(user_id, "pro")

    return "invalid_action"


# =========================
# フル自動運用（管理用）
# =========================
def run_full_cycle():
    log_event("FULL_SAAS_CYCLE_START")

    generate_ranking()
    generate_ctr_titles()
    generate_seo_report()
    build_growth_report()
    run_rewrite()
    run_internal_linking()
    build_dashboard()

    log_event("FULL_SAAS_CYCLE_END")

    return "full_cycle_done"