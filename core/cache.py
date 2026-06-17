import json
import os


class Cache:

    def __init__(self):

        self.path = "data/cache.json"
        self.data = self._load()

    # =========================
    # 読み込み
    # =========================
    def _load(self):

        if not os.path.exists(self.path):
            return {}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    # =========================
    # 保存
    # =========================
    def _save(self):

        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # =========================
    # 取得
    # =========================
    def get(self, key: str):

        return self.data.get(key)

    # =========================
    # 設定
    # =========================
    def set(self, key: str, value: str):

        self.data[key] = value
        self._save()