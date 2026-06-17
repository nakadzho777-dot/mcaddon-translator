import os
import json
import zipfile


class MCAddonBuilder:

    def rebuild_from_folder(self, input_root: str, output_root: str):

        for root, _, files in os.walk(input_root):
            for f in files:

                if not f.endswith(".json"):
                    continue

                in_path = os.path.join(root, f)
                rel = os.path.relpath(in_path, input_root)
                out_path = os.path.join(output_root, rel)

                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                try:
                    with open(in_path, "r", encoding="utf-8") as r:
                        data = json.load(r)

                    tmp = out_path + ".tmp"

                    with open(tmp, "w", encoding="utf-8") as w:
                        json.dump(data, w, ensure_ascii=False, indent=2)

                    os.replace(tmp, out_path)

                except:
                    pass

    def build_mcaddon(self, folder: str, output_file: str):

        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as z:

            for root, _, files in os.walk(folder):
                for f in files:
                    full = os.path.join(root, f)
                    arc = os.path.relpath(full, folder)
                    z.write(full, arc)