import json
import os


class Config:

    def __init__(self, path="config.json"):
        self.path = path
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return {
                "model": "gpt-4o-mini",
                "max_workers": 4,
                "language": "ja",
                "enable_cache": True
            }

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)