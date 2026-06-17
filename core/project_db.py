
import json
import os
import uuid
from datetime import datetime

from core.rbac import can_edit, can_delete_project

PROJECT_FILE = "data/projects.json"


def load():
    if not os.path.exists(PROJECT_FILE):
        return {}

    with open(PROJECT_FILE, "r") as f:
        return json.load(f)


def save(data):
    with open(PROJECT_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# プロジェクト作成
# =========================
def create_project(username: str, team_id: str, name: str):

    data = load()

    if team_id not in data:
        data[team_id] = {}

    project_id = str(uuid.uuid4())

    data[team_id][project_id] = {
        "name": name,
        "owner": username,
        "created_at": datetime.utcnow().isoformat(),
        "files": {},
        "history": []
    }

    save(data)

    return project_id


# =========================
# 編集チェック
# =========================
def can_user_edit(team_id: str, username: str):

    return can_edit(team_id, username)


# =========================
# 削除チェック
# =========================
def can_user_delete(team_id: str, username: str):

    return can_delete_project(team_id, username)