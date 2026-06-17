import json
import urllib.request
import zipfile
import os
import shutil


class Updater:

    def __init__(self, version="1.0.0"):
        self.version = version
        self.url = "https://example.com/version.json"

    # ----------------------------
    # 更新チェック
    # ----------------------------

    def check_update(self):

        try:
            with urllib.request.urlopen(self.url) as r:
                data = json.loads(r.read().decode())

            latest = data["version"]

            if latest != self.version:
                return {
                    "update": True,
                    "version": latest,
                    "url": data["url"]
                }

            return {"update": False}

        except:
            return {"update": False}

    # ----------------------------
    # ダウンロード
    # ----------------------------

    def download(self, url, path="update.zip"):

        try:
            urllib.request.urlretrieve(url, path)
            return path
        except:
            return None

    # ----------------------------
    # 展開更新
    # ----------------------------

    def apply_update(self, zip_path):

        try:
            temp_dir = "update_tmp"

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(temp_dir)

            # exeの場所を取得
            base_dir = os.path.dirname(os.path.abspath(__file__))

            for root, _, files in os.walk(temp_dir):
                for f in files:
                    src = os.path.join(root, f)
                    rel = os.path.relpath(src, temp_dir)
                    dst = os.path.join(base_dir, rel)

                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)

            shutil.rmtree(temp_dir)
            return True

        except:
            return False