import json
import urllib.request
from datetime import datetime


class LicenseManager:

    def __init__(self):
        self.url = "https://example.com/licenses.json"

    def verify(self, key: str):

        try:
            with urllib.request.urlopen(self.url) as r:
                data = json.loads(r.read().decode())

            if key not in data:
                return False

            lic = data[key]

            if not lic["active"]:
                return False

            # 有効期限チェック
            expire = datetime.strptime(lic["expire"], "%Y-%m-%d")

            if datetime.now() > expire:
                return False

            return True

        except:
            return False