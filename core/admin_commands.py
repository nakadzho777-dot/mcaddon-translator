from core.logger import log_event
from core.config_center import set_value, get
from core.deployment_manager import deploy, rollback
from core.task_queue import start_workers


# =========================
# 管理者コマンド実行
# =========================
def execute_admin_command(command: str, params: dict = None):
    params = params or {}

    log_event(f"ADMIN_COMMAND {command}")

    commands = {
        "restart_workers": lambda: start_workers(params.get("count", 2)),

        "set_config": lambda: set_value(
            params["key"],
            params["value"]
        ),

        "get_config": lambda: get(params["key"]),

        "deploy": lambda: deploy(params["build_path"]),

        "rollback": lambda: rollback(params["build_path"]),

        "shutdown": lambda: {"status": "SYSTEM_SHUTDOWN_REQUESTED"},
    }

    func = commands.get(command)

    if not func:
        return {"error": "UNKNOWN_ADMIN_COMMAND"}

    try:
        result = func()
        log_event(f"ADMIN_OK {command}")
        return result

    except Exception as e:
        log_event(f"ADMIN_FAIL {command} {e}", level="ERROR")
        return {"error": str(e)}


# =========================
# 危険操作チェック
# =========================
def is_dangerous(command: str):
    return command in ["shutdown", "rollback", "deploy"]


# =========================
# 安全実行ラッパー
# =========================
def safe_admin_execute(command: str, params: dict = None, is_admin: bool = False):
    if is_dangerous(command) and not is_admin:
        log_event(f"ADMIN_BLOCKED {command}", level="WARNING")
        return {"error": "NOT_AUTHORIZED"}

    return execute_admin_command(command, params)