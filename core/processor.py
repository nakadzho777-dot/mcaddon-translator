import os
import json

from core.job_manager import JobManager
from core.checkpoint import CheckpointManager
from core.logger import Logger


class MCAddonProcessor:

    def __init__(self):
        self.job_manager = JobManager(max_workers=4)
        self.checkpoint = CheckpointManager()
        self.logger = Logger()
        self.files = []

    def scan(self, root_path: str):

        targets = []

        for root, _, files in os.walk(root_path):
            for f in files:

                if not f.endswith(".json"):
                    continue

                path = os.path.join(root, f)

                if "lang" in f.lower() or "text" in f.lower():

                    if not self.checkpoint.is_done(path):
                        targets.append(path)

        self.files = targets
        return targets

    def run(self, translator, progress_callback=None):

        self.job_manager.queue.queue.clear()

        for file_path in self.files:
            self.job_manager.add_job(self._process_file, file_path, translator)

        if progress_callback:
            self.job_manager.set_progress_callback(progress_callback)

        return self.job_manager.run()

    def _process_file(self, file_path: str, translator):

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return {"file": file_path, "error": "invalid format"}

            keys = []
            texts = []

            for k, v in data.items():
                if isinstance(v, str):
                    keys.append(k)
                    texts.append(v)

            try:
                translated = translator.translate_batch_fast(texts)
            except Exception as e:
                self.logger.error(f"batch error {file_path}: {e}")
                translated = texts

            changed = False

            for k, new_text in zip(keys, translated):
                if data[k] != new_text:
                    data[k] = new_text
                    changed = True

            if changed:
                tmp = file_path + ".tmp"

                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                os.replace(tmp, file_path)

            self.checkpoint.mark_done(file_path)

            return {"file": file_path, "changed": changed}

        except Exception as e:
            self.logger.error(str(e))
            return {"file": file_path, "error": str(e)}