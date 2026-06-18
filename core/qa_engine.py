from core.logger import log_event
from core.self_healing import safe_run
from core.analytics_engine import track_event


# =========================
# テストケース実行
# =========================
def run_test_case(name: str, func, *args, **kwargs):
    try:
        result = safe_run(name, func, *args, **kwargs)

        log_event(f"TEST_PASS {name}")
        return {"test": name, "status": "PASS", "result": result}

    except Exception as e:
        log_event(f"TEST_FAIL {name} {e}", level="ERROR")
        return {"test": name, "status": "FAIL", "error": str(e)}


# =========================
# スモークテスト（基本動作確認）
# =========================
def smoke_test(system_map: dict):
    results = []

    for name, func in system_map.items():
        results.append(run_test_case(name, func))

    return {
        "type": "smoke",
        "results": results
    }


# =========================
# 回帰テスト（重要機能）
# =========================
def regression_test(core_functions: dict):
    results = []

    for name, func in core_functions.items():
        result = run_test_case(name, func)

        if result["status"] == "FAIL":
            log_event(f"REGRESSION_FAIL {name}", level="CRITICAL")

        results.append(result)

    return {
        "type": "regression",
        "results": results
    }


# =========================
# 自動品質スコア
# =========================
def calculate_quality_score(test_results: dict):
    all_tests = test_results.get("results", [])

    if not all_tests:
        return 0

    passed = len([t for t in all_tests if t["status"] == "PASS"])

    return (passed / len(all_tests)) * 100


# =========================
# フルQA実行
# =========================
def run_full_qa(system_map: dict, core_functions: dict):
    smoke = smoke_test(system_map)
    regression = regression_test(core_functions)

    total = smoke["results"] + regression["results"]

    score = calculate_quality_score({"results": total})

    track_event("system", "qa_run")

    return {
        "smoke": smoke,
        "regression": regression,
        "quality_score": score
    }