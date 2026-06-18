from core.logger import log_event
from core.ux_orchestrator import update_state


# =========================
# ステップ定義
# =========================
ONBOARDING_STEPS = [
    "welcome",
    "setup_profile",
    "first_action",
    "show_result",
    "complete"
]


# =========================
# 初期化
# =========================
def start_onboarding(user_id: str):
    update_state(user_id, {
        "onboarding_step": "welcome",
        "progress": 0
    })

    log_event(f"ONBOARDING_START {user_id}")

    return {"status": "started"}


# =========================
# 次ステップへ
# =========================
def next_step(user_id: str, current_step: str):
    if current_step not in ONBOARDING_STEPS:
        return {"error": "invalid_step"}

    index = ONBOARDING_STEPS.index(current_step)

    if index + 1 >= len(ONBOARDING_STEPS):
        update_state(user_id, {
            "onboarding_step": "complete",
            "progress": 100
        })

        log_event(f"ONBOARDING_COMPLETE {user_id}")

        return {"status": "completed"}

    next_step_name = ONBOARDING_STEPS[index + 1]

    progress = int((index + 1) / len(ONBOARDING_STEPS) * 100)

    update_state(user_id, {
        "onboarding_step": next_step_name,
        "progress": progress
    })

    log_event(f"ONBOARDING_STEP {user_id} {next_step_name}")

    return {
        "status": "next",
        "step": next_step_name,
        "progress": progress
    }


# =========================
# 現在状態取得
# =========================
def get_onboarding(user_id: str):
    return {
        "state": "active"
    }


# =========================
# 強制完了
# =========================
def force_complete(user_id: str):
    update_state(user_id, {
        "onboarding_step": "complete",
        "progress": 100
    })

    log_event(f"ONBOARDING_FORCE_COMPLETE {user_id}")

    return {"status": "forced_complete"}