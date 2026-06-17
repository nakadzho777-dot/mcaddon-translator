
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
import os
import stripe

# =========================
# core
# =========================
from core.users_db import init_users, login_user
from core.plan_manager import init_plans, set_plan
from core.team_db import init_teams, create_team, add_member
from core.project_db import create_project
from core.rbac import can_edit
from core.update_manager import init_update
from core.log_manager import init_logs, add_log

# realtime
from core.realtime import manager

# notifications
from core.notifications import send_slack, send_email, push_notification

# UI
from services.admin_dashboard import app as admin_app
from services.log_dashboard import app as log_app
from services.ui_app import app as ui_app


app = FastAPI()


# =========================
# 初期化
# =========================
init_users()
init_plans()
init_teams()
init_update()
init_logs()


# =========================
# WebSocket
# =========================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =========================
# ログイン
# =========================
@app.post("/login")
async def login(data: dict):

    token = login_user(data["username"], data["password"])

    add_log(data["username"], "LOGIN")

    push_notification(data["username"], "ログインしました")

    send_slack(f"{data['username']} logged in")

    await manager.broadcast({
        "type": "log",
        "action": "LOGIN",
        "user": data["username"]
    })

    if not token:
        return {"error": "invalid login"}

    return {"token": token}


# =========================
# プロジェクト作成
# =========================
@app.post("/project/create")
async def api_create_project(data: dict):

    if not can_edit(data["team_id"], data["username"]):

        add_log(data["username"], "PROJECT_DENIED")

        push_notification(data["username"], "権限がありません")

        return {"error": "permission denied"}

    project_id = create_project(
        data["username"],
        data["team_id"],
        data["name"]
    )

    add_log(data["username"], "PROJECT_CREATE")

    push_notification(data["username"], "プロジェクト作成完了")

    send_slack(f"Project created by {data['username']}")

    await manager.broadcast({
        "type": "project",
        "action": "CREATE",
        "project_id": project_id
    })

    return {"project_id": project_id}


# =========================
# チーム作成
# =========================
@app.post("/team/create")
async def api_create_team(data: dict):

    team_id = create_team(data["username"], data["name"])

    add_log(data["username"], "TEAM_CREATE")

    push_notification(data["username"], "チーム作成完了")

    send_slack(f"Team created: {team_id}")

    await manager.broadcast({
        "type": "team",
        "action": "CREATE",
        "team_id": team_id
    })

    return {"team_id": team_id}


# =========================
# アップデート
# =========================
@app.post("/update/check")
def check_update(data: dict):

    latest = {"version": "1.0.0"}

    return {
        "latest": latest["version"],
        "update": False
    }


# =========================
# DASHBOARD
# =========================
app.mount("/admin", admin_app)
app.mount("/logs", log_app)
app.mount("/", ui_app)