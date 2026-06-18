import os
import time

from core.logger import log_event
from tools.auto_blog_generator import generate_article
from core.ranking_engine import generate_ranking
from core.rewrite_engine import run_rewrite
from core.seo_optimizer import generate_seo_report
from core.internal_linker import run_internal_linking
from core.ctr_optimizer import generate_ctr_titles


# =========================
# 自動運用エンジン
# =========================
def run_cycle():
    log_event("AUTO_CYCLE_START")

    print("🚀 記事生成...")
    # 新規記事生成は別途キーワードで回す想定
    # generate_article("sample keyword")

    print("📊 ランキング更新...")
    generate_ranking()

    print("🔁 CTR改善...")
    generate_ctr_titles()

    print("🔍 SEO分析...")
    generate_seo_report()

    print("✍️ リライト...")
    run_rewrite()

    print("🔗 内部リンク構築...")
    run_internal_linking()

    log_event("AUTO_CYCLE_END")

    print("✅ 自動改善ループ完了")


# =========================
# ループ実行
# =========================
def run_forever(interval=3600):
    while True:
        try:
            run_cycle()
        except Exception as e:
            log_event(f"AUTO_ERROR {e}", level="ERROR")
            print("❌ エラー:", e)

        print(f"⏳ 次回実行まで {interval}秒")
        time.sleep(interval)


# =========================
# 実行
# =========================
if __name__ == "__main__":
    run_forever()