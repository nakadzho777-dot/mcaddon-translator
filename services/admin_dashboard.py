from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json
import os

app = FastAPI()


USER_FILE = "data/users.json"
TEAM_FILE = "data/teams.json"
PROJECT_FILE = "data/projects.json"


# =========================
# データ読み込み
# =========================
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


# =========================
# 管理ダッシュボードUI
# =========================
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():

    users = load_json(USER_FILE)
    teams = load_json(TEAM_FILE)
    projects = load_json(PROJECT_FILE)

    total_users = len(users)
    pro_users = sum(1 for u in users.values() if u.get("plan") == "PRO")
    total_teams = len(teams)
    total_projects = sum(len(v) for v in projects.values())

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Admin Dashboard</title>

    <style>
        body {{
            font-family: Arial;
            background: #0f172a;
            color: white;
            margin: 0;
        }}

        .container {{
            padding: 30px;
        }}

        .card {{
            background: #1f2937;
            padding: 20px;
            margin: 10px;
            border-radius: 10px;
            display: inline-block;
            width: 200px;
        }}

        .value {{
            font-size: 28px;
            font-weight: bold;
        }}
    </style>
</head>

<body>

<div class="container">

    <h1>🛠 Admin Dashboard</h1>

    <div class="card">
        <div>Users</div>
        <div class="value">{total_users}</div>
    </div>

    <div class="card">
        <div>PRO Users</div>
        <div class="value">{pro_users}</div>
    </div>

    <div class="card">
        <div>Teams</div>
        <div class="value">{total_teams}</div>
    </div>

    <div class="card">
        <div>Projects</div>
        <div class="value">{total_projects}</div>
    </div>

</div>

</body>
</html>
"""