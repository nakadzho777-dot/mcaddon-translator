
import json
import os
import uuid
from datetime import datetime

TEAM_FILE = "data/teams.json"


def init_teams():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(TEAM_FILE):
        with open(TEAM_FILE, "w") as f:
            json.dump({}, f)


def load():
    with open(TEAM_FILE, "r") as f:
        return json.load(f)


def save(data):
    with open(TEAM_FILE, "w") as f:
        json.dump(data, f, indent=2)


# =========================
# チーム作成
# =========================
def create_team(owner: str, name: str):

    data = load()

    team_id = str(uuid.uuid4())

    data[team_id] = {
        "name": name,
        "owner": owner,
        "members": {
            owner: "OWNER"
        },
        "created_at": datetime.utcnow().isoformat()
    }

    save(data)

    return team_id


# =========================
# メンバー追加（権限付き）
# =========================
def add_member(team_id: str, username: str, role: str = "MEMBER"):

    data = load()

    if team_id not in data:
        return False

    data[team_id]["members"][username] = role

    save(data)

    return True


# =========================
# チーム取得
# =========================
def get_team(team_id: str):

    data = load()

    return data.get(team_id)