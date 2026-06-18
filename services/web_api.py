import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="MCAddon Translator API")

BLOG_DIR = "landing/blog"
LANDING_DIR = "landing"


@app.get("/")
def home():
    index_path = os.path.join(LANDING_DIR, "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")

    return HTMLResponse("""
    <html>
    <head><title>MCAddon Translator</title></head>
    <body>
        <h1>MCAddon Translator</h1>
        <p>Minecraftアドオン翻訳ツール</p>
        <p><a href="/blog/">Blog</a></p>
    </body>
    </html>
    """)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sitemap.xml")
def sitemap():
    path = os.path.join(LANDING_DIR, "sitemap.xml")

    if not os.path.exists(path):
        return PlainTextResponse(
            '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
            media_type="application/xml"
        )

    return FileResponse(path, media_type="application/xml")


@app.get("/robots.txt")
def robots():
    content = """User-agent: *
Allow: /

Sitemap: https://mcaddon-translator-production.up.railway.app/sitemap.xml
"""
    return PlainTextResponse(content, media_type="text/plain")


if os.path.exists(BLOG_DIR):
    app.mount("/blog", StaticFiles(directory=BLOG_DIR, html=True), name="blog")