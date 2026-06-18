import os
import json
from datetime import datetime
from collections import Counter

from fastapi import FastAPI, Query
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    Response,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="MCAddon Translator")

LANDING_DIR = "landing"
BLOG_DIR = "landing/blog"
SITEMAP_PATH = "landing/sitemap.xml"
CLICK_LOG = "data/clicks.json"

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def record_click(source: str, target: str):
    os.makedirs("data", exist_ok=True)

    try:
        with open(CLICK_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    data.append({
        "time": datetime.now().isoformat(),
        "source": source,
        "target": target,
    })

    with open(CLICK_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_clicks():
    try:
        with open(CLICK_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def admin_login_page():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>Admin Login</title>
</head>
<body>
<h1>管理ページ</h1>
<form method="get">
<input type="password" name="password" placeholder="password">
<button type="submit">ログイン</button>
</form>
</body>
</html>
""", status_code=401)


def check_admin(password: str):
    return password == ADMIN_PASSWORD


@app.get("/")
def home():
    path = os.path.join(LANDING_DIR, "index.html")

    if os.path.exists(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")

    return HTMLResponse("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>MCAddon Translator</title>
</head>
<body>
<h1>MCAddon Translator</h1>
<p><a href="/blog/">ブログを見る</a></p>
<p><a href="/pricing">料金プランを見る</a></p>
</body>
</html>
""")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/click")
def click(
    source: str = Query(default="unknown"),
    target: str = Query(default="/")
):
    record_click(source, target)
    return RedirectResponse(url=target)


@app.get("/admin/clicks")
def admin_clicks(password: str = Query(default="")):
    if not check_admin(password):
        return admin_login_page()

    clicks = load_clicks()

    rows = ""

    for item in reversed(clicks[-200:]):
        rows += f"""
<tr>
<td>{item.get("time", "")}</td>
<td>{item.get("source", "")}</td>
<td>{item.get("target", "")}</td>
</tr>
"""

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>クリックログ</title>
</head>
<body>
<h1>クリックログ</h1>

<p><a href="/admin/dashboard?password={password}">管理ダッシュボードへ</a></p>

<p>合計クリック数: {len(clicks)}</p>

<table border="1" cellpadding="6">
<tr>
<th>Time</th>
<th>Source</th>
<th>Target</th>
</tr>
{rows}
</table>

</body>
</html>
""")


@app.get("/admin/dashboard")
def admin_dashboard(password: str = Query(default="")):
    if not check_admin(password):
        return admin_login_page()

    clicks = load_clicks()

    source_counts = Counter([c.get("source", "unknown") for c in clicks])
    target_counts = Counter([c.get("target", "unknown") for c in clicks])

    source_rows = ""

    for source, count in source_counts.most_common():
        source_rows += f"""
<tr>
<td>{source}</td>
<td>{count}</td>
</tr>
"""

    target_rows = ""

    for target, count in target_counts.most_common():
        target_rows += f"""
<tr>
<td>{target}</td>
<td>{count}</td>
</tr>
"""

    recent_rows = ""

    for item in reversed(clicks[-20:]):
        recent_rows += f"""
<tr>
<td>{item.get("time", "")}</td>
<td>{item.get("source", "")}</td>
<td>{item.get("target", "")}</td>
</tr>
"""

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>管理ダッシュボード</title>
</head>
<body>

<h1>管理ダッシュボード</h1>

<p>総クリック数: <strong>{len(clicks)}</strong></p>

<h2>Source別クリック</h2>
<table border="1" cellpadding="6">
<tr>
<th>Source</th>
<th>Clicks</th>
</tr>
{source_rows}
</table>

<h2>Target別クリック</h2>
<table border="1" cellpadding="6">
<tr>
<th>Target</th>
<th>Clicks</th>
</tr>
{target_rows}
</table>

<h2>最近のクリック</h2>
<table border="1" cellpadding="6">
<tr>
<th>Time</th>
<th>Source</th>
<th>Target</th>
</tr>
{recent_rows}
</table>

<p><a href="/admin/clicks?password={password}">クリックログ詳細へ</a></p>
<p><a href="/">トップへ戻る</a></p>

</body>
</html>
""")


@app.get("/pricing")
def pricing():
    path = os.path.join(LANDING_DIR, "pricing.html")

    if os.path.exists(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")

    return HTMLResponse("<h1>料金ページはまだ生成されていません。</h1>")


@app.get("/pricing/")
def pricing_slash():
    return pricing()


@app.get("/blog/")
def blog_index():
    path = os.path.join(BLOG_DIR, "index.html")

    if os.path.exists(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")

    return HTMLResponse("<h1>ブログ一覧</h1>")


@app.get("/sitemap.xml")
def sitemap():
    if os.path.exists(SITEMAP_PATH):
        with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
            xml = f.read().strip()

        return Response(
            content=xml,
            media_type="application/xml; charset=utf-8",
        )

    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
        media_type="application/xml; charset=utf-8",
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