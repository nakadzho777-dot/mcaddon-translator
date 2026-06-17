
from core.team_db import get_team


# =========================
# 権限取得
# =========================
def get_role(team_id: str, username: str):

    team = get_team(team_id)

    if not team:
        return None

    return team["members"].get(username)


# =========================
# 権限チェック
# =========================
def require_role(team_id: str, username: str, allowed_roles: list):

    role = get_role(team_id, username)

    if role is None:
        return False

    return role in allowed_roles


# =========================
# 操作別チェック
# =========================
def can_edit(team_id: str, username: str):

    return require_role(team_id, username, ["OWNER", "ADMIN", "MEMBER"])


def can_manage_team(team_id: str, username: str):

    return require_role(team_id, username, ["OWNER", "ADMIN"])


def can_delete_project(team_id: str, username: str):

    return require_role(team_id, username, ["OWNER"])