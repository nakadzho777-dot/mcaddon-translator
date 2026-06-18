import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

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
from core.blog_index import generate_blog_index


OUTPUT_DIR = "landing/blog"
KEYWORD_PATH = "data/keywords.json"
MAX_WORKERS = 3
MAX_ARTICLES_PER_RUN = 20

DEFAULT_KEYWORDS = [
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


def load_keywords():
    if os.path.exists(KEYWORD_PATH):
        try:
            with open(KEYWORD_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list) and data:
                print(f"📚 keywords.json 読み込み: {len(data)}件")
                return data

        except Exception as e:
            print("⚠ keywords.json 読み込み失敗:", repr(e))

    print("📚 DEFAULT_KEYWORDS を使用")
    return DEFAULT_KEYWORDS


def already_generated(keyword: str) -> bool:
    try:
        seo = generate_seo(keyword)
        filename = f"{seo['slug']}.html"
        return os.path.exists(os.path.join(OUTPUT_DIR, filename))
    except Exception:
        return False


def generate_article(keyword: str):
    print(f"🚀 生成開始: {keyword}")
    log_event(f"START {keyword}")

    seo = generate_seo(keyword)
    filename = f"{seo['slug']}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(filepath):
        print(f"⏭ 既存スキップ: {filename}")
        return filename

    body = generate_article_body(keyword)

    score = score_article(keyword, seo["title"], body)
    print(f"📊 初期SEOスコア: {score}/100 - {keyword}")

    if score < 70:
        print(f"🔧 リライト実行: {keyword}")
        body = rewrite_if_needed(keyword, seo["title"], body, score)
        score = score_article(keyword, seo["title"], body)
        print(f"📊 改善後SEOスコア: {score}/100 - {keyword}")

    ensure_dir(OUTPUT_DIR)

    html = build_html(seo, body, score)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    log_event(f"CREATED {filename} SCORE {score}")
    print(f"✅ 生成完了: {filename}")

    return filename


def collect_existing_files():
    ensure_dir(OUTPUT_DIR)

    return [
        f for f in os.listdir(OUTPUT_DIR)
        if f.endswith(".html") and f != "index.html"
    ]


def run_parallel(keywords):
    generated = []

    print("🔥 並列SEO生成開始")

    targets = []

    for kw in keywords:
        if len(targets) >= MAX_ARTICLES_PER_RUN:
            break

        targets.append(kw)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_article, keyword): keyword
            for keyword in targets
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

    keywords = load_keywords()
    files = run_parallel(keywords)

    existing_files = collect_existing_files()
    all_files = sorted(set(existing_files + files))

    print(f"📄 総記事数: {len(all_files)}")

    generate_blog_index()

    update_sitemap(all_files)

    run_internal_linking()

    generate_blog_index()

    log_event("COMPLETE ALL")
    print("✅ キーワード拡張SEO生成 完了")


if __name__ == "__main__":
    main()