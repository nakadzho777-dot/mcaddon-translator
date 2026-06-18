import os
from datetime import datetime

SITE_URL = os.getenv(
    "SITE_URL",
    "https://mcaddon-translator-production.up.railway.app"
)

SITEMAP_PATHS = [
    "landing/sitemap.xml",
    "landing/blog/sitemap.xml",
]


def update_sitemap(files):
    today = datetime.now().strftime("%Y-%m-%d")

    urls = ""

    # ブログ一覧ページも登録
    urls += f"""  <url>
    <loc>{SITE_URL}/blog/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
"""

    for f in files:
        if not f:
            continue

        urls += f"""  <url>
    <loc>{SITE_URL}/blog/{f}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>
"""

    for path in SITEMAP_PATHS:
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)

    print("✅ sitemap.xml 更新完了")