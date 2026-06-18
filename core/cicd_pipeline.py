import os
import subprocess
from datetime import datetime

from core.logger import log_event
from core.release_manager import apply_release, get_current_version


# =========================
# テスト実行
# =========================
def run_tests():
    log_event("CI_TEST_START")

    result = subprocess.run(["echo", "running tests"], capture_output=True, text=True)

    if result.returncode != 0:
        log_event("CI_TEST_FAILED", level="ERROR")
        return False

    log_event("CI_TEST_SUCCESS")
    return True


# =========================
# ビルド処理
# =========================
def build_project():
    log_event("CI_BUILD_START")

    try:
        os.system("echo building project")
        log_event("CI_BUILD_SUCCESS")
        return True

    except Exception as e:
        log_event(f"CI_BUILD_FAILED {e}", level="ERROR")
        return False


# =========================
# デプロイ
# =========================
def deploy(version: str):
    log_event(f"DEPLOY_START {version}")

    success = apply_release(version, previous_version=get_current_version())

    if success["status"] == "success":
        log_event(f"DEPLOY_SUCCESS {version}")
        return True

    log_event(f"DEPLOY_FAILED {version}", level="ERROR")
    return False


# =========================
# フルパイプライン
# =========================
def run_pipeline(new_version: str):
    log_event(f"PIPELINE_START {new_version}")

    if not run_tests():
        return {"status": "failed", "step": "tests"}

    if not build_project():
        return {"status": "failed", "step": "build"}

    if not deploy(new_version):
        return {"status": "failed", "step": "deploy"}

    log_event(f"PIPELINE_SUCCESS {new_version}")

    return {"status": "success"}