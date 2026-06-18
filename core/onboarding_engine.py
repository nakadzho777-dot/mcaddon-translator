from core.logger import log_event
from core.analytics_engine import track_event


# =========================
# ステップ定義
# =========================
ONBOARDING_STEPS = [
    "welcome",
    "project_create",
    "upload_addon",
    "auto_translate",
    "preview_result",
    "upgrade_prompt"
]


# =========================
# ステップ取得
# =========================
def get_next_step(current_step: str):
    if current_step not in ONBOARDING_STEPS:
        return ONBOARDING_STEPS[0]

    idx = ONBOARDING_STEPS.index(current_step)

    if idx + 1 >= len(ONBOARDING_STEPS):
        return None

    return ONBOARDING_STEPS[idx + 1]


# =========================
# ステップ実行記録
# =========================
def complete_step(user_id: str, step: str):
    track_event(user_id, f"onboarding_{step}")
    log_event(f"ONBOARDING {user_id} {step}")


# =========================
# 離脱防止ロジック
# =========================
def detect_drop_off(user_events: list):
    completed = set(user_events)

    missing = [s for s in ONBOARDING_STEPS if s not in completed]

    return {
        "completed_steps": len(completed),
        "missing_steps": missing,
        "risk": "HIGH" if len(missing) > 2 else "LOW"
    }


# =========================
# 初回価値提示
# =========================
def show_first_value():
    return {
        "message": "Minecraftアドオンをドラッグするだけで日本語化できます",
        "cta": "今すぐ無料で試す"
    }


# =========================
# アップグレード誘導
# =========================
def upgrade_prompt(user_plan: str):
    if user_plan == "free":
        return {
            "message": "Proにすると高速翻訳＆SEO生成が解放されます",
            "cta": "アップグレード"
        }

    return None