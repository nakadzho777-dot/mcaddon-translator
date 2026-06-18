from core.logger import log_event
from core.security_engine import secure_execute
from core.analytics_engine import track_event
from core.audit_engine import record_action


# =========================
# ルーティング定義
# =========================
ROUTES = {}


# =========================
# ルート登録
# =========================
def register_route(name: str, action: str, func):
    ROUTES[name] = {
        "action": action,
        "func": func
    }

    log_event(f"ROUTE_REGISTERED {name}")


# =========================
# API実行
# =========================
def call_api(user_id: str, route: str, *args, **kwargs):
    if route not in ROUTES:
        return {"error": "ROUTE_NOT_FOUND"}

    endpoint = ROUTES[route]
    action = endpoint["action"]
    func = endpoint["func"]

    # セキュア実行（権限・レート制限）
    result = secure_execute(user_id, action, func, *args, **kwargs)

    # トラッキング
    track_event(user_id, f"api_call_{route}")

    # 監査ログ
    record_action(user_id, action, route, kwargs)

    return result


# =========================
# API一覧取得
# =========================
def list_routes():
    return list(ROUTES.keys())


# =========================
# 初期ルートセット（例）
# =========================
def init_default_routes(core_modules):
    """
    core_modules例:
    {
        "generate": func,
        "seo": func,
        "dashboard": func
    }
    """

    for name, func in core_modules.items():
        register_route(name, name, func)