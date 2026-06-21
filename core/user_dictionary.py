import json
import os

USER_DICT_PATH = "data/user_dictionary.json"


class UserDictionary:

    def __init__(self):
        self.path = USER_DICT_PATH
        self.data = {}
        self.load()

    def ensure_file(self):
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def load(self):
        self.ensure_file()

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}

    def save(self):
        os.makedirs("data", exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get(self, key: str):
        if not key:
            return None

        return self.data.get(key)

    def set(self, key: str, value: str):
        key = key.strip()
        value = value.strip()

        if not key or not value:
            return False

        self.data[key] = value
        self.save()
        return True

    def delete(self, key: str):
        if key in self.data:
            del self.data[key]
            self.save()
            return True

        return False

    def all(self):
        return self.data

    def search(self, keyword: str):
        keyword = keyword.lower().strip()

        if not keyword:
            return self.data

        return {
            k: v
            for k, v in self.data.items()
            if keyword in k.lower() or keyword in v.lower()
        }