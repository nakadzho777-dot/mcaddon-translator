import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, Response, PlainTextResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="MCAddon Translator")

LANDING_DIR = "landing"
BLOG_DIR = "landing/blog"
SITEMAP_PATH = "landing/sitemap.xml"


@app.get("/")
def home():
    index_path = os.path.join(LANDING_DIR, "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html; charset=utf-8")

    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>MCAddon Translator</title>
</head>
<body>
<h1>MCAddon Translator</h1>
<p>Minecraftアドオン翻訳ツール</p>
<p><a href="/blog/">ブログを見る</a></p>
<p><a href="/pricing">料金プランを見る</a></p>
</body>
</html>
""")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/pricing")
def pricing():
    return pricing_page()


@app.get("/pricing/")
def pricing_slash():
    return pricing_page()


def pricing_page():
    path = os.path.join(LANDING_DIR, "pricing.html")

    if os.path.exists(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")

    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>料金プラン | MCAddon Translator</title>
</head>
<body>
<h1>MCAddon Translator 料金プラン</h1>
<p>料金ページはまだ生成されていません。</p>
<p><a href="/">トップへ戻る</a></p>
</body>
</html>
""")


@app.get("/blog/")
def blog_index():
    index_path = os.path.join(BLOG_DIR, "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html; charset=utf-8")

    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>ブログ一覧</title>
</head>
<body>
<h1>ブログ一覧</h1>
<p>まだ記事一覧が生成されていません。</p>
</body>
</html>
""")


@app.get("/sitemap.xml")
def sitemap():
    if os.path.exists(SITEMAP_PATH):
        with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
            xml = f.read().strip()

        if xml.startswith("<?xml") or xml.startswith("<urlset"):
            return Response(
                content=xml,
                media_type="application/xml; charset=utf-8"
            )

    fallback_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>
"""
    return Response(
        content=fallback_xml,
        media_type="application/xml; charset=utf-8"
    )


@app.get("/robots.txt")
def robots():
    content = """User-agent: *
Allow: /

Sitemap: https://mcaddon-translator-production.up.railway.app/sitemap.xml
"""
    return PlainTextResponse(content, media_type="text/plain; charset=utf-8")


if os.path.exists(BLOG_DIR):
    app.mount("/blog", StaticFiles(directory=BLOG_DIR, html=True), name="blog-static")