import os
import json
import csv
import io
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

from services.stripe_payments import router as billing_router
from core.license_store import create_license

app = FastAPI(title="MCAddon Translator")
app.include_router(billing_router)

LANDING_DIR = "landing"
BLOG_DIR = "landing/blog"
SITEMAP_PATH = "landing/sitemap.xml"
CLICK_LOG = "data/clicks.json"
LICENSE_DB = "data/licenses.json"

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def record_click(source: str, target: str):
    data = load_json(CLICK_LOG, [])
    data.append({
        "time": datetime.now().isoformat(),
        "source": source,
        "target": target,
    })
    save_json(CLICK_LOG, data)


def load_clicks():
    return load_json(CLICK_LOG, [])


def load_licenses():
    return load_json(LICENSE_DB, {})


def check_admin(password: str):
    return password == ADMIN_PASSWORD


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


@app.get("/")
def home():
    path = os.path.join(LANDING_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path, media_type="text/html; charset=utf-8")

    return HTMLResponse("<h1>MCAddon Translator</h1>")


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


@app.get("/admin/dashboard")
def admin_dashboard(password: str = Query(default="")):
    if not check_admin(password):
        return admin_login_page()

    clicks = load_clicks()
    licenses = load_licenses()

    source_counts = Counter([c.get("source", "unknown") for c in clicks])
    target_counts = Counter([c.get("target", "unknown") for c in clicks])

    source_rows = "".join(
        f"<tr><td>{source}</td><td>{count}</td></tr>"
        for source, count in source_counts.most_common()
    )

    target_rows = "".join(
        f"<tr><td>{target}</td><td>{count}</td></tr>"
        for target, count in target_counts.most_common()
    )

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>管理ダッシュボード</title></head>
<body>
<h1>管理ダッシュボード</h1>

<p>総クリック数: <strong>{len(clicks)}</strong></p>
<p>発行済みライセンス数: <strong>{len(licenses)}</strong></p>

<p><a href="/admin/clicks?password={password}">クリックログ詳細</a></p>
<p><a href="/admin/clicks.csv?password={password}">クリックCSV</a></p>
<p><a href="/admin/licenses?password={password}">ライセンス管理</a></p>

<h2>Source別クリック</h2>
<table border="1" cellpadding="6">
<tr><th>Source</th><th>Clicks</th></tr>
{source_rows}
</table>

<h2>Target別クリック</h2>
<table border="1" cellpadding="6">
<tr><th>Target</th><th>Clicks</th></tr>
{target_rows}
</table>

</body>
</html>
""")


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
<h1>クリックログ</h1>
<p><a href="/admin/dashboard?password={password}">ダッシュボードへ</a></p>
<p>合計クリック数: {len(clicks)}</p>
<table border="1" cellpadding="6">
<tr><th>Time</th><th>Source</th><th>Target</th></tr>
{rows}
</table>
""")


@app.get("/admin/clicks.csv")
def admin_clicks_csv(password: str = Query(default="")):
    if not check_admin(password):
        return PlainTextResponse("Unauthorized", status_code=401)

    clicks = load_clicks()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["time", "source", "target"])

    for item in clicks:
        writer.writerow([
            item.get("time", ""),
            item.get("source", ""),
            item.get("target", ""),
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=clicks.csv"}
    )


@app.get("/admin/licenses")
def admin_licenses(password: str = Query(default="")):
    if not check_admin(password):
        return admin_login_page()

    licenses = load_licenses()
    rows = ""

    for key, item in reversed(list(licenses.items())):
        rows += f"""
<tr>
<td><code>{key}</code></td>
<td>{item.get("email", "")}</td>
<td>{item.get("plan", "")}</td>
<td>{item.get("status", "")}</td>
<td>{item.get("source", "")}</td>
<td>{item.get("created_at", "")}</td>
</tr>
"""

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>ライセンス管理</title></head>
<body>

<h1>ライセンス管理</h1>
<p>発行済みライセンス数: {len(licenses)}</p>

<p><a href="/admin/dashboard?password={password}">ダッシュボードへ</a></p>
<p><a href="/admin/create-license?password={password}&email=test@example.com">テストライセンス発行</a></p>

<table border="1" cellpadding="6">
<tr>
<th>License Key</th>
<th>Email</th>
<th>Plan</th>
<th>Status</th>
<th>Source</th>
<th>Created At</th>
</tr>
{rows}
</table>

</body>
</html>
""")


@app.get("/admin/create-license")
def admin_create_license(
    password: str = Query(default=""),
    email: str = Query(default="test@example.com")
):
    if not check_admin(password):
        return admin_login_page()

    key = create_license(email=email, source="manual_admin")

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>ライセンス発行</title></head>
<body>
<h1>テストライセンス発行完了</h1>
<p>Email: {email}</p>
<p>License Key:</p>
<pre style="font-size:20px; border:1px solid #ccc; padding:12px;">{key}</pre>
<p><a href="/admin/licenses?password={password}">ライセンス管理へ戻る</a></p>
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

        return Response(content=xml, media_type="application/xml; charset=utf-8")

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