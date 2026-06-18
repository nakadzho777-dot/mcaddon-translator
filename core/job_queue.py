import time
import threading
from queue import Queue

from core.logger import log_event


# =========================
# ジョブキュー本体
# =========================
job_queue = Queue()
workers_running = True


# =========================
# ジョブ追加
# =========================
def add_job(job_type: str, payload: dict):
    job = {
        "type": job_type,
        "payload": payload,
        "time": time.time()
    }

    job_queue.put(job)

    log_event(f"JOB_ADDED {job_type}")


# =========================
# ジョブ実行ロジック
# =========================
def process_job(job: dict):
    job_type = job["type"]

    log_event(f"JOB_START {job_type}")

    # ダミー処理（ここに実処理を接続）
    time.sleep(1)

    log_event(f"JOB_DONE {job_type}")


# =========================
# ワーカー
# =========================
def worker():
    while workers_running:
        try:
            job = job_queue.get(timeout=1)
            process_job(job)
            job_queue.task_done()

        except:
            continue


# =========================
# ワーカー起動
# =========================
def start_workers(count: int = 2):
    for _ in range(count):
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    log_event(f"WORKERS_STARTED {count}")


# =========================
# 状態確認
# =========================
def queue_status():
    return {
        "queue_size": job_queue.qsize()
    }