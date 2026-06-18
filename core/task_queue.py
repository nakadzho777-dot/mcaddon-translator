import time
import threading
from queue import Queue

from core.logger import log_event
from core.self_healing import safe_run


# =========================
# グローバルキュー
# =========================
TASK_QUEUE = Queue()


# =========================
# タスク登録
# =========================
def add_task(name: str, func, *args, **kwargs):
    TASK_QUEUE.put((name, func, args, kwargs))
    log_event(f"TASK_QUEUED {name}")


# =========================
# ワーカー処理
# =========================
def worker_loop():
    while True:
        try:
            name, func, args, kwargs = TASK_QUEUE.get()

            log_event(f"TASK_START {name}")

            safe_run(name, func, *args, **kwargs)

            log_event(f"TASK_DONE {name}")

            TASK_QUEUE.task_done()

        except Exception as e:
            log_event(f"TASK_ERROR {name} {e}", level="ERROR")

        time.sleep(0.1)


# =========================
# ワーカー起動
# =========================
def start_workers(count: int = 2):
    for i in range(count):
        t = threading.Thread(target=worker_loop, daemon=True)
        t.start()

        log_event(f"WORKER_STARTED {i+1}")


# =========================
# キュー状態確認
# =========================
def get_queue_size():
    return TASK_QUEUE.qsize()