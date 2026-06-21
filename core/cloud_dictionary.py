import json
import os
import urllib.request


class CloudDictionary:
    """
    Railwayクラウド辞書クライアント。

    現在の安全設定:
    - translate() はローカル辞書のみ参照
      ※ RailwayのSSLタイムアウト対策
    - add() はRailwayへ保存し、成功/失敗に関係なくローカルにも保存
    - stats() / export() は管理画面用にRailwayへ問い合わせ
    """

    FILE = "data/cloud_dictionary.json"
    CONFIG = "data/config.json"

    def __init__(self):
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.FILE):
            with open(self.FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        self.server_url = ""
        self.api_key = ""
        self.reload()

    def reload(self):
        self.server_url = ""
        self.api_key = ""

        try:
            with open(self.CONFIG, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.server_url = str(
                data.get("cloud_dictionary_url", "")
            ).strip().rstrip("/")

            self.api_key = str(
                data.get("cloud_dictionary_api_key", "")
            ).strip()

        except Exception:
            self.server_url = ""
            self.api_key = ""

    def load(self):
        try:
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save(self, data):
        os.makedirs("data", exist_ok=True)

        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def translate(self, text):
        """
        SSLタイムアウト対策として、今はクラウド検索を使わずローカル辞書だけ使う。
        後で「手動同期」方式に変更予定。
        """
        text = str(text or "").strip()

        if not text:
            return None

        return self.load().get(text)

    def add(self, source, translated):
        source = str(source or "").strip()
        translated = str(translated or "").strip()

        if not source or not translated:
            return False

        self.reload()

        print("===== CLOUD SAVE =====")
        print("SOURCE:", source[:50])
        print("URL:", self.server_url)

        server_ok = False

        if self.server_url:
            server_ok = self._server_add(source, translated)
            print("SERVER RESULT:", server_ok)

        self._local_add(source, translated)

        return True

    def stats(self):
        """
        Railway /stats を取得。
        失敗時はローカル辞書の件数を返す。
        """
        self.reload()

        if self.server_url:
            data = self._server_get("/stats")
            if isinstance(data, dict):
                return data

        local = self.load()

        return {
            "total": len(local),
            "top": [],
            "mode": "local"
        }

    def export(self):
        """
        Railway /export を取得。
        失敗時はローカル辞書を返す。
        """
        self.reload()

        if self.server_url:
            data = self._server_get("/export")
            if isinstance(data, dict):
                return data

        return self.load()

    def sync_from_server(self):
        """
        サーバー辞書をローカルへ取り込む。
        """
        data = self.export()

        if not isinstance(data, dict):
            return False

        current = self.load()
        current.update(data)
        self.save(current)

        return True

    def _local_add(self, source, translated):
        data = self.load()
        data[source] = translated
        self.save(data)

    def _headers(self):
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        return headers

    def _server_get(self, path):
        try:
            req = urllib.request.Request(
                self.server_url + path,
                method="GET",
                headers=self._headers()
            )

            with urllib.request.urlopen(req, timeout=8) as res:
                body = res.read().decode("utf-8", errors="replace")

            return json.loads(body)

        except Exception as e:
            print("CLOUD GET ERROR:", e)
            return None

    def _server_add(self, source, translated):
        try:
            payload = json.dumps(
                {
                    "source": source,
                    "translated": translated
                },
                ensure_ascii=False
            ).encode("utf-8")

            req = urllib.request.Request(
                self.server_url + "/add",
                data=payload,
                method="POST",
                headers=self._headers()
            )

            with urllib.request.urlopen(req, timeout=8) as res:
                body = res.read().decode("utf-8", errors="replace")

            data = json.loads(body)
            return bool(data.get("ok"))

        except Exception as e:
            print("CLOUD ADD ERROR:", e)
            return False
