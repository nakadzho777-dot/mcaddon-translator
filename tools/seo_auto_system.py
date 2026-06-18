import os
import json
import random
from datetime import datetime

OUTPUT_DIR = "landing/blog"
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.json")
SITEMAP_FILE = os.path.join(OUTPUT_DIR, "sitemap.xml")

BASE_KEYWORDS = [
    "minecraft アドオン 翻訳",
    "minecraft addon 日本語化",
    "mcaddon 変換 方法",
    "minecraft mod 翻訳",
    "minecraft addon エラー 修正",
    "minecraft addon 作り方",
]

MODIFIERS = [
    "初心者向け",
    "2026年版",
    "完全ガイド",
    "最速方法",
    "無料ツール",
    "自動化"
]

def slugify(text):
    return text.replace(" ", "-")

def load_index():
    if os.path.exists(INDEX_FILE):
        return json.load(open(INDEX_FILE, "r", encoding="utf-8"))
    return []

def save_index(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json.dump(data, open(INDEX_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def build_sitemap(files):
    urls = ""
    for f in files:
        urls += f"""
    <url>
        <loc>https://your-domain.com/blog/{f}</loc>
        <lastmod>{datetime.utcnow().date()}</lastmod>
    </url>
"""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset>{urls}
</urlset>"""
    open(SITEMAP_FILE, "w", encoding="utf-8").write(xml)

def generate_article(title):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>

<body style="font-family:Arial; background:#0f172a; color:white; padding:40px;">

<h1>{title}</h1>

<p>Minecraftアドオンの作業は複雑ですが、自動化できます。</p>

<h2>解決策</h2>
<p>MCAddon Translator SaaSを使うことで効率化できます。</p>

<ul>
<li>自動翻訳</li>
<li>エラー修正</li>
<li>ファイル変換</li>
</ul>

<h2>手順</h2>
<ol>
<li>アップロード</li>
<li>自動処理</li>
<li>ダウンロード</li>
</ol>

<h2>今すぐ試す</h2>
<a href="/" style="color:#60a5fa;">無料で使う</a>

</body>
</html>
"""

def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    index = load_index()
    existing = set(index)

    new_files = []

    for base in BASE_KEYWORDS:
        for mod in MODIFIERS:

            title = f"{base} {mod}"
            filename = slugify(title) + ".html"

            if filename in existing:
                continue

            path = os.path.join(OUTPUT_DIR, filename)

            with open(path, "w", encoding="utf-8") as f:
                f.write(generate_article(title))

            index.append(filename)
            new_files.append(filename)

            print("generated:", filename)

    save_index(index)
    build_sitemap(index)

    print("DONE:", len(new_files), "new articles")

if __name__ == "__main__":
    generate()