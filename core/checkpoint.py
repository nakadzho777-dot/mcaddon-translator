import json
import os


class CheckpointManager:
    """
    進捗保存・再開管理
    """

    def __init__(self, path="checkpoint.json"):
        self.path = path
        self.data = self._load()

    # ----------------------------
    # load
    # ----------------------------

    def _load(self):
        if not os.path.exists(self.path):
            return {
                "processed_files": [],
                "last_index": 0
            }

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ----------------------------
    # save
    # ----------------------------

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ----------------------------
    # file完了記録
    # ----------------------------

    def mark_done(self, file_path: str):
        if file_path not in self.data["processed_files"]:
            self.data["processed_files"].append(file_path)

        self._save()

    # ----------------------------
    # 処理済み判定
    # ----------------------------

    def is_done(self, file_path: str) -> bool:
        return file_path in self.data["processed_files"]

    # ----------------------------
    # リセット
    # ----------------------------

    def reset(self):
        self.data = {
            "processed_files": [],
            "last_index": 0
        }
        self._save()