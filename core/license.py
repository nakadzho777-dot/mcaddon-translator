import json
import os
import uuid
import requests

LICENSE_CACHE = "license.json"

VERIFY_URL = (
    "https://mcaddon-translator-production.up.railway.app"
    "/billing/verify"
)


class LicenseManager:

    def __init__(self):
        self.pc_id = self.get_pc_id()

    def get_pc_id(self):
        return str(uuid.getnode())

    def save_cache(self, key):
        data = {
            "license_key": key,
            "pc_id": self.pc_id
        }

        with open(LICENSE_CACHE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_cache(self):
        if not os.path.exists(LICENSE_CACHE):
            return None

        try:
            with open(LICENSE_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def verify_online(self, key):

        try:
            r = requests.get(
                VERIFY_URL,
                params={"key": key},
                timeout=15
            )

            data = r.json()

            if not data.get("valid"):
                return False

            self.save_cache(key)
            return True

        except Exception:
            return False

    def verify(self, key):

        # オンライン認証
        if self.verify_online(key):
            return True

        # オフラインキャッシュ
        cache = self.load_cache()

        if not cache:
            return False

        if cache.get("license_key") != key:
            return False

        if cache.get("pc_id") != self.pc_id:
            return False

        return True