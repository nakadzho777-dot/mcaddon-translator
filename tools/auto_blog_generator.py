import os
import re
from datetime import datetime
from openai import OpenAI

from core.logger import log_event
from core.internal_linker import run_internal_linking

# =========================
# 設定
# =========================
BASE_URL = "https://github.com/nakadzho777-dot/mcaddon-translator"
OUTPUT_DIR = "landing/blog"
SITEMAP_PATH = "landing/blog/sitemap.xml"

MODEL = "gpt-4o-mini"

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY が設定されていません")

client = OpenAI(api_key=api_key)

# =========================
# キーワード
# =========================
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

# =========================
# ユーティリティ
# =========================
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


# =========================
# SEO分析
# =========================
def analyze_keyword(keyword: str) -> str:
    prompt = f"""
キーワード:
{keyword}

検索意図・ユーザー層・攻略方針を簡潔に分析してください。
"""

    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content


# =========================
# 構成生成
# =========================
def generate_structure(keyword: str, analysis: str) -> str:
    prompt = f"""
キーワード:
{keyword}

分析:
{analysis}

h2 / h3構造で記事構成を作成してください（5〜8章）。
"""

    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content


# =========================
# 本文生成
# =========================
def generate_body(keyword: str, structure: str) -> str:
    prompt = f"""
以下の構成でSEO記事を作成してください。

キーワード: {keyword}

構成:
{structure}

条件:
- 2000〜3000文字
- 初心者向け
- 実用的手順重視
"""

    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content


# =========================
# SEO生成
# =========================
def generate_seo(keyword: str) -> dict:
    prompt = f"""
SEO情報をJSONで出力:

キーワード: {keyword}

形式:
{{
  "title": "...",
  "description": "...",
  "slug": "..."
}}
"""

    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    try:
        return json.loads(res.choices[0].message.content)
    except:
        return {
            "title": f"【2026年最新版】{keyword}",
            "description": keyword,
            "slug": slugify(keyword),
        }


# =========================
# HTML生成
# =========================
def build_html(seo: dict, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{seo['title']}</title>
<meta name="description" content="{seo['description']}">
</head>
<body>

<h1>{seo['title']}</h1>

{body}

<hr>
<p><a href="/">👉 翻訳ツールはこちら</a></p>

</body>
</html>
"""


# =========================
# 記事生成
# =========================
def generate_article(keyword: str) -> str:
    print(f"🚀 生成中: {keyword}")
    log_event(f"START {keyword}")

    analysis = analyze_keyword(keyword)
    structure = generate_structure(keyword, analysis)
    body = generate_body(keyword, structure)
    seo = generate_seo(keyword)

    filename = f"{seo['slug']}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    ensure_dir(OUTPUT_DIR)

    html = build_html(seo, body)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    log_event(f"CREATED {filename}")

    return filename


# =========================
# sitemap更新
# =========================
def update_sitemap(files):
    urls = ""

    for f in files:
        urls += f"<url><loc>{BASE_URL}/blog/{f}</loc></url>\n"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""

    ensure_dir(os.path.dirname(SITEMAP_PATH))

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(xml)


# =========================
# 実行
# =========================
if __name__ == "__main__":
    generated = []

    for kw in KEYWORDS:
        try:
            file = generate_article(kw)
            generated.append(file)
        except Exception as e:
            log_event(f"ERROR {kw} {e}")
            print(f"❌ エラー: {kw}")

    update_sitemap(generated)

    # 🔥 内部リンク自動生成（統合）
    run_internal_linking()

    log_event("COMPLETE ALL")
    print("✅ 完全自動SEO生成完了")