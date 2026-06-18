import os
from openai import OpenAI
from datetime import datetime

# =========================
# 設定
# =========================
BASE_URL = "https://github.com/nakadzho777-dot/mcaddon-translator"  # ←変更する
OUTPUT_DIR = "landing/blog"

# APIキー
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY が設定されていません")

client = OpenAI(api_key=api_key)

# =========================
# キーワード（増やすほど強い）
# =========================
keywords = [
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
# スラッグ生成
# =========================
def slugify(text):
    return text.lower().replace(" ", "-")

# =========================
# 記事生成
# =========================
def generate_content(keyword):
    prompt = f"""
以下のキーワードでSEO記事を書いてください。

キーワード: {keyword}

条件:
・2000文字以上
・見出し付き（h2, h3）
・初心者向け
・具体的な手順あり
・自然な日本語
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return res.choices[0].message.content

# =========================
# HTML生成
# =========================
def generate_article(keyword):
    print(f"生成中: {keyword}")

    content = generate_content(keyword)

    slug = slugify(keyword)
    filename = f"{slug}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    title = f"【2026年最新版】{keyword}｜初心者でも簡単にできる"

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="description" content="{keyword}のやり方を解説">
</head>
<body>

<h1>{title}</h1>

{content}

<p><a href="/">👉 翻訳ツールはこちら</a></p>

</body>
</html>
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filename

# =========================
# sitemap更新
# =========================
def update_sitemap(filenames):
    urls = ""
    for name in filenames:
        urls += f"<url><loc>{BASE_URL}/blog/{name}</loc></url>\n"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml)

# =========================
# 実行
# =========================
if __name__ == "__main__":
    generated_files = []

    for kw in keywords:
        try:
            file = generate_article(kw)
            generated_files.append(file)
        except Exception as e:
            print(f"エラー（{kw}）: {e}")

    update_sitemap(generated_files)

    print("✅ 記事生成＆sitemap更新 完了🔥")