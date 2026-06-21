import json
import os
import urllib.request
import webbrowser


class UpdateChecker:
    """
    Railwayの /version API を見て、最新版があるか確認します。
    """

    CONFIG = "data/config.json"
    CURRENT_VERSION = "1.0.0"

    def __init__(self):
        self.version_url = ""

    def load_config(self):
        if not os.path.exists(self.CONFIG):
            return {}

        try:
            with open(self.CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_current_version(self):
        data = self.load_config()
        return str(data.get("app_version", self.CURRENT_VERSION))

    def get_version_url(self):
        data = self.load_config()

        # 既存のRailway URLを流用
        base_url = str(data.get("update_server_url", "")).strip().rstrip("/")

        if not base_url:
            base_url = str(data.get("cloud_dictionary_url", "")).strip().rstrip("/")

        if not base_url:
            return ""

        return base_url + "/version"

    def check(self):
        current = self.get_current_version()
        url = self.get_version_url()

        if not url:
            return {
                "ok": False,
                "update_available": False,
                "current": current,
                "latest": current,
                "message": "更新サーバーURLが未設定です。"
            }

        try:
            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=6) as res:
                body = res.read().decode("utf-8", errors="replace")

            data = json.loads(body)

            latest = str(data.get("version", current))
            notes = data.get("notes", [])
            download_url = str(data.get("download_url", ""))

            return {
                "ok": True,
                "update_available": self._is_newer(latest, current),
                "current": current,
                "latest": latest,
                "notes": notes,
                "download_url": download_url,
                "raw": data
            }

        except Exception as e:
            return {
                "ok": False,
                "update_available": False,
                "current": current,
                "latest": current,
                "message": str(e)
            }

    def open_download(self, url):
        if url:
            webbrowser.open(url)

    def _is_newer(self, latest, current):
        try:
            latest_parts = self._version_parts(latest)
            current_parts = self._version_parts(current)
            return latest_parts > current_parts
        except Exception:
            return latest != current

    def _version_parts(self, text):
        parts = []
        for p in str(text).split("."):
            try:
                parts.append(int(p))
            except Exception:
                parts.append(0)

        while len(parts) < 3:
            parts.append(0)

        return tuple(parts[:3])
