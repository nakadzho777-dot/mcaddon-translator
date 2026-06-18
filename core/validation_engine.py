import traceback

from core.logger import log_event


# =========================
# 単体テスト実行
# =========================
def run_test(name, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)

        log_event(f"TEST_PASS {name}")

        return {"test": name, "status": "PASS", "result": result}

    except Exception as e:
        log_event(f"TEST_FAIL {name} {e}", level="ERROR")

        return {
            "test": name,
            "status": "FAIL",
            "error": str(e),
            "trace": traceback.format_exc()
        }


# =========================
# システム検証
# =========================
def validate_system(checks: dict):
    results = {}

    for name, func in checks.items():
        try:
            results[name] = run_test(name, func)

        except Exception as e:
            results[name] = {
                "status": "CRASH",
                "error": str(e)
            }

    return results


# =========================
# デプロイ前チェック
# =========================
def pre_deploy_check(checks: dict):
    results = validate_system(checks)

    failed = [k for k, v in results.items() if v.get("status") != "PASS"]

    if failed:
        log_event(f"DEPLOY_BLOCKED {failed}", level="ERROR")

        return {
            "status": "BLOCKED",
            "failed": failed,
            "details": results
        }

    log_event("DEPLOY_ALLOWED")

    return {
        "status": "OK",
        "details": results
    }


# =========================
# ヘルススコア
# =========================
def system_health_score(results: dict):
    total = len(results)
    passed = len([r for r in results.values() if r.get("status") == "PASS"])

    if total == 0:
        return 0

    return (passed / total) * 100