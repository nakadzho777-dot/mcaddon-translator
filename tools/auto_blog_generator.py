import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================
# project root path fix
# =========================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from core.logger import log_event
from core.seo_engine import (
    generate_seo,
    generate_article_body,
    score_article,
    rewrite_if_needed,
)
from core.html_builder import build_html
from core.sitemap import update_sitemap
from core.internal_linker import run_internal_linking


OUTPUT_DIR = "landing/blog"
MAX_WORKERS = 3

KEYWORDS = [
    "mcaddon 翻訳 やり方",
    "mcaddon 日本語化 方法",
    "minecraft addon 日本語にする方法",
    "mcpack 日本語化 手順",
    "minecraft json 翻訳 やり方",
    "minecraft アドオン 翻訳 ツール",
    "mcaddon lang ファイル 編集",
    "mcaddon 翻訳 エラー 解決",
    "minecraft addon 日本語にならない",
    "mcpack 翻訳できない 原因",
]


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def generate_article(keyword: str):
    print(f"🚀 生成開始: {keyword}")
    log_event(f"START {keyword}")

    seo = generate_seo(keyword)
    body = generate_article_body(keyword)

    score = score_article(keyword, seo["title"], body)
    print(f"📊 初期SEOスコア: {score}/100 - {keyword}")

    if score < 70:
        print(f"🔧 リライト実行: {keyword}")
        body = rewrite_if_needed(keyword, seo["title"], body, score)
        score = score_article(keyword, seo["title"], body)
        print(f"📊 改善後SEOスコア: {score}/100 - {keyword}")

    ensure_dir(OUTPUT_DIR)

    filename = f"{seo['slug']}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    html = build_html(seo, body, score)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    log_event(f"CREATED {filename} SCORE {score}")
    print(f"✅ 生成完了: {filename}")

    return filename


def run_parallel():
    generated = []

    print("🔥 並列SEO生成開始")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_article, keyword): keyword
            for keyword in KEYWORDS
        }

        for future in as_completed(futures):
            keyword = futures[future]

            try:
                result = future.result()
                if result:
                    generated.append(result)

            except Exception as e:
                print(f"❌ エラー: {keyword}")
                print("詳細:", repr(e))
                log_event(f"ERROR {keyword} {repr(e)}", level="ERROR")

    return generated


def main():
    print("🚀 AUTO BLOG GENERATOR PRODUCTION START")

    files = run_parallel()

    print(f"📄 生成記事数: {len(files)}")

    update_sitemap(files)

    run_internal_linking()

    log_event("COMPLETE ALL")
    print("✅ 完全プロダクションSEO生成 完了")


if __name__ == "__main__":
    main()