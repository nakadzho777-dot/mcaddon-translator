from core.logger import log_event
from core.job_queue import add_job
from core.cache_manager import get_cache, set_cache


# =========================
# UI状態管理
# =========================
UI_STATE = {}


# =========================
# 状態更新
# =========================
def update_state(user_id: str, state: dict):
    UI_STATE[user_id] = state

    set_cache(f"ui_state:{user_id}", state, ttl=600)

    log_event(f"UI_STATE_UPDATED {user_id}")


# =========================
# 状態取得
# =========================
def get_state(user_id: str):
    cached = get_cache(f"ui_state:{user_id}")

    if cached:
        return cached

    return UI_STATE.get(user_id, {})


# =========================
# 処理開始（UIトリガー）
# =========================
def start_process(user_id: str, process_type: str, payload: dict):
    update_state(user_id, {
        "status": "processing",
        "process": process_type
    })

    add_job(process_type, {
        "user_id": user_id,
        "payload": payload
    })

    return {
        "status": "started",
        "process": process_type
    }


# =========================
# 成功状態
# =========================
def mark_success(user_id: str, result: dict):
    update_state(user_id, {
        "status": "success",
        "result": result
    })

    log_event(f"PROCESS_SUCCESS {user_id}")


# =========================
# 失敗状態
# =========================
def mark_failed(user_id: str, error: str):
    update_state(user_id, {
        "status": "failed",
        "error": error
    })

    log_event(f"PROCESS_FAILED {user_id} {error}")


# =========================
# UXレスポンス統一
# =========================
def get_response(user_id: str):
    state = get_state(user_id)

    if not state:
        return {"status": "idle"}

    return state