import time
import traceback

from core.logger import log_event


# =========================
# 安全実行ラッパー
# =========================
def safe_execute(func, *args, retries=3, delay=3, **kwargs):
    """
    関数を安全に実行（リトライ付き）
    """

    for attempt in range(retries):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            log_event(f"ERROR {func.__name__} attempt {attempt+1} {e}", level="ERROR")
            print(f"⚠️ エラー発生: {func.__name__} retry {attempt+1}")

            time.sleep(delay)

    log_event(f"FAILED {func.__name__}", level="ERROR")
    return None


# =========================
# バッチ安全実行
# =========================
def safe_batch_execute(func_list):
    results = []

    for func, args, kwargs in func_list:
        result = safe_execute(func, *args, **kwargs)
        results.append(result)

    return results


# =========================
# 監視ログ付き実行
# =========================
def monitored_run(name, func, *args, **kwargs):
    log_event(f"RUN_START {name}")

    start = time.time()

    try:
        result = func(*args, **kwargs)
        duration = time.time() - start

        log_event(f"RUN_SUCCESS {name} {duration:.2f}s")

        return result

    except Exception as e:
        duration = time.time() - start

        log_event(f"RUN_FAIL {name} {e} {duration:.2f}s", level="ERROR")

        print(f"❌ 実行失敗: {name}")

        return None