from core.logger import log_event
from core.security_manager import authorize


# =========================
# API定義（契約）
# =========================
API_CONTRACTS = {
    "translate": {
        "action": "translate",
        "permission": "translate"
    },
    "export_project": {
        "action": "export",
        "permission": "export"
    },
    "create_project": {
        "action": "write",
        "permission": "manage"
    },
    "get_stats": {
        "action": "read",
        "permission": "read"
    }
}


# =========================
# API呼び出し統一入口
# =========================
def call_api(user_id: str, role: str, endpoint: str, payload: dict = None):
    if endpoint not in API_CONTRACTS:
        log_event(f"API_NOT_FOUND {endpoint}", level="ERROR")
        return {"error": "invalid_endpoint"}

    contract = API_CONTRACTS[endpoint]

    auth = authorize(user_id, role, contract["permission"])

    if auth["status"] != "allowed":
        return auth

    log_event(f"API_CALL {user_id} {endpoint}")

    return execute(endpoint, payload or {})


# =========================
# 実行ロジック分岐
# =========================
def execute(endpoint: str, payload: dict):
    if endpoint == "translate":
        return {"result": "translated_text_placeholder"}

    if endpoint == "export_project":
        return {"result": "exported_file.zip"}

    if endpoint == "create_project":
        return {"result": "project_created"}

    if endpoint == "get_stats":
        return {"result": {"users": 100, "revenue": 500}}

    return {"error": "not_implemented"}