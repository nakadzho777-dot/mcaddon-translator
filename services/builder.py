import os
import zipfile
import uuid


# =========================
# mcaddonビルダー
# =========================
class MCAddonBuilder:

    def __init__(self, base_path="data/builds"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    # =========================
    # プロジェクト → ZIP化
    # =========================
    def build_zip(self, project_data, project_name: str):

        build_id = str(uuid.uuid4())
        output_path = os.path.join(self.base_path, f"{project_name}_{build_id}.mcaddon")

        zipf = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)

        files = project_data.get("files", {})

        # -------------------------
        # mcaddon構造を書き込み
        # -------------------------
        for path, content in files.items():
            zipf.writestr(path, content)

        zipf.close()

        return output_path