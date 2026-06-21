import json
import os


class JsonRepair:
    def scan(self, root_path):
        results = []
        if not root_path or not os.path.exists(root_path):
            return results

        base = os.path.dirname(root_path) if os.path.isfile(root_path) else root_path

        for root, _, files in os.walk(base):
            for file in files:
                if not file.lower().endswith(".json"):
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        json.load(f)
                except Exception as e:
                    results.append({"file": path, "error": str(e)})
        return results

    def repair(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            # よくあるJSON破損だけを安全寄りに修正
            fixed = text.replace(",}", "}").replace(",]", "]")

            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(fixed)
            return True
        except Exception:
            return False
