import threading
import queue
import time
from dataclasses import dataclass
from typing import Callable, Any, Optional


@dataclass
class JobResult:
    success: bool
    result: Any = None
    error: Optional[str] = None


class Job:
    def __init__(self, func: Callable, args=(), kwargs=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.result: Optional[JobResult] = None


class JobManager:
    """
    システム全体の処理統括クラス
    - 翻訳バッチ処理
    - 進捗管理
    - キャンセル
    """

    def __init__(self, max_workers: int = 1):
        self.queue = queue.Queue()
        self.results = []
        self.max_workers = max_workers

        self._stop_event = threading.Event()
        self._workers = []
        self._progress_callback = None

    # ----------------------------
    # public API
    # ----------------------------

    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """(done, total)"""
        self._progress_callback = callback

    def add_job(self, func: Callable, *args, **kwargs):
        self.queue.put(Job(func, args, kwargs))

    def run(self):
        self._stop_event.clear()
        self.results.clear()

        total = self.queue.qsize()
        done = 0

        def worker():
            nonlocal done

            while not self._stop_event.is_set():
                try:
                    job: Job = self.queue.get_nowait()
                except queue.Empty:
                    return

                try:
                    result = job.func(*job.args, **job.kwargs)
                    job.result = JobResult(True, result=result)

                except Exception as e:
                    job.result = JobResult(False, error=str(e))

                self.results.append(job.result)

                done += 1

                if self._progress_callback:
                    self._progress_callback(done, total)

                self.queue.task_done()

        # worker起動
        self._workers = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            self._workers.append(t)

        # 完了待機
        for t in self._workers:
            t.join()

        return self.results

    def stop(self):
        """処理キャンセル"""
        self._stop_event.set()