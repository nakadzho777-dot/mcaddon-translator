from core.logger import log_event
from core.analytics_engine import track_event
from core.self_healing import safe_run
from core.alert_system import trigger_alert
from core.validation_engine import validate_system


# =========================
# 実行パイプライン
# =========================
def run_pipeline(user_id: str, pipeline: list):
    results = {}

    for step in pipeline:
        name = step["name"]
        func = step["func"]
        args = step.get("args", [])
        kwargs = step.get("kwargs", {})

        def wrapped():
            return func(*args, **kwargs)

        result = safe_run(name, wrapped)

        results[name] = result

        track_event(user_id, f"pipeline_{name}")

    return results


# =========================
# 自動最適実行
# =========================
def auto_orchestrate(user_id: str, tasks: dict):
    """
    tasks例:
    {
        "generate": func,
        "seo": func,
        "publish": func
    }
    """

    log_event("ORCHESTRATION_START")

    # ① システム健全性チェック
    health = validate_system(tasks)

    failed = [k for k, v in health.items() if v.get("status") != "PASS"]

    if failed:
        trigger_alert("WARNING", "PIPELINE_DEGRADED", {"failed": failed})

    # ② 実行順序（シンプル優先度）
    order = sorted(tasks.items(), key=lambda x: 0 if "generate" in x[0] else 1)

    pipeline = [
        {"name": name, "func": func}
        for name, func in order
    ]

    return run_pipeline(user_id, pipeline)


# =========================
# 自動リカバリ付き実行
# =========================
def resilient_orchestrate(user_id: str, tasks: dict):
    try:
        return auto_orchestrate(user_id, tasks)

    except Exception as e:
        log_event(f"ORCHESTRATION_FAIL {e}", level="ERROR")

        trigger_alert("CRITICAL", "ORCHESTRATION_FAILED", {"error": str(e)})

        return {"status": "FAILED", "fallback": True}