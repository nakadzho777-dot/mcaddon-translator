import os
import shutil
from datetime import datetime

from core.logger import log_event
from core.qa_engine import run_full_qa
from core.alert_engine import trigger_alert


# =========================
# ビルド実行
# =========================
def build_project(source_dir: str, build_dir: str):
    try:
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)

        shutil.copytree(source_dir, build_dir)

        log_event("BUILD_SUCCESS")

        return True

    except Exception as e:
        log_event(f"BUILD_FAIL {e}", level="ERROR")
        return False


# =========================
# デプロイ準備
# =========================
def prepare_release(version: str):
    release_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_event(f"RELEASE_PREP {version}")

    return {
        "release_id": release_id,
        "version": version
    }


# =========================
# フルテスト→ビルド→リリース
# =========================
def deploy_pipeline(system_map: dict, core_functions: dict, source_dir: str, build_dir: str, version: str):
    log_event("PIPELINE_START")

    # ① QA
    qa_result = run_full_qa(system_map, core_functions)

    if qa_result["quality_score"] < 80:
        trigger_alert(
            "CRITICAL",
            "QA failed - deployment blocked",
            qa_result
        )
        return {"status": "blocked", "reason": "qa_failed"}

    # ② ビルド
    if not build_project(source_dir, build_dir):
        trigger_alert("CRITICAL", "Build failed")
        return {"status": "failed", "reason": "build_failed"}

    # ③ リリース準備
    release = prepare_release(version)

    log_event("DEPLOY_SUCCESS")

    return {
        "status": "success",
        "release": release,
        "qa": qa_result
    }


# =========================
# ロールバック
# =========================
def rollback_release(previous_version_dir: str, target_dir: str):
    try:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        shutil.copytree(previous_version_dir, target_dir)

        log_event("ROLLBACK_SUCCESS")

        return True

    except Exception as e:
        log_event(f"ROLLBACK_FAIL {e}", level="ERROR")
        return False