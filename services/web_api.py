from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
load_dotenv()

from services.stripe_payments import router as billing_router
from core.db import init_db, get_conn

# =========================
# APP
# =========================

app = FastAPI(title="MCAddon SaaS (Production Ready)")

init_db()
app.include_router(billing_router)

# =========================
# ENV
# =========================

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

BASE_URL = os.getenv(
    "BASE_URL",
    "https://mcaddon-translator-production.up.railway.app"
)

# =========================
# AUTH (JWT)
# =========================

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return None


def get_user(auth: str = Header(None)):
    if not auth:
        raise HTTPException(401, "Missing token")

    token = auth.replace("Bearer ", "")
    data = verify_token(token)

    if not data:
        raise HTTPException(401, "Invalid token")

    return data["user"]

# =========================
# MODELS
# =========================

class Auth(BaseModel):
    username: str
    password: str

class Project(BaseModel):
    name: str
    description: str = ""

# =========================
# UI
# =========================

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style="font-family:Arial;background:#0f172a;color:white;padding:40px;">
        <h1>MCAddon SaaS</h1>
        <p>Production Running ✔</p>

        <a href="/landing" style="color:#60a5fa;">Landing</a><br>
        <a href="/blog/minecraft-addon-translation.html" style="color:#60a5fa;">SEO Blog</a><br>
        <a href="/sitemap.xml" style="color:#60a5fa;">Sitemap</a><br>
        <a href="/google281c3da749cf0393.html" style="color:#60a5fa;">Google Verify</a><br>
        <a href="/docs" style="color:#60a5fa;">API Docs</a>
    </body>
    </html>
    """

# =========================
# LANDING
# =========================

@app.get("/landing")
def landing():
    return FileResponse("landing/index.html")

# =========================
# BLOG（SEO）
# =========================

@app.get("/blog/{filename}")
def blog(filename: str):
    path = f"landing/blog/{filename}"
    if not os.path.exists(path):
        raise HTTPException(404, "Not found")
    return FileResponse(path)

# =========================
# SITEMAP
# =========================

@app.get("/sitemap.xml")
def sitemap():
    path = "landing/blog/sitemap.xml"
    if not os.path.exists(path):
        raise HTTPException(404, "sitemap not found")

    return FileResponse(path, media_type="application/xml")

# =========================
# GOOGLE VERIFICATION
# =========================

@app.get("/google281c3da749cf0393.html")
def google_verify():
    return PlainTextResponse(
        "google-site-verification: google281c3da749cf0393.html"
    )

# =========================
# AUTH API
# =========================

@app.post("/register")
def register(req: Auth):

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (req.username, req.password, "free")
        )
        conn.commit()
    except:
        raise HTTPException(400, "User exists")

    conn.close()
    return {"status": "registered"}


@app.post("/login")
def login(req: Auth):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT password FROM users WHERE username=?",
        (req.username,)
    )

    row = cur.fetchone()
    conn.close()

    if not row or row[0] != req.password:
        raise HTTPException(401, "Invalid login")

    token = create_token({"user": req.username})

    return {
        "access_token": token
    }

# =========================
# PROJECT
# =========================

@app.post("/project/create")
def create_project(req: Project, user: str = Depends(get_user)):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO projects VALUES (NULL, ?, ?, ?, ?)",
        (user, req.name, req.description, datetime.utcnow().isoformat())
    )

    conn.commit()
    conn.close()

    return {"status": "created"}

# =========================
# ADMIN
# =========================

@app.get("/admin/stats")
def stats():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects")
    projects = cur.fetchone()[0]

    conn.close()

    return {
        "users": users,
        "projects": projects
    }