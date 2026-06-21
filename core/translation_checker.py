import os
import json
import re


class TranslationChecker:
    def __init__(self):
        self.issues = []

    def check(self, root_path):
        self.issues = []

        if not root_path or not os.path.exists(root_path):
            return self.issues

        folder = os.path.dirname(root_path) if os.path.isfile(root_path) else root_path

        for root, _, files in os.walk(folder):
            for name in files:
                path = os.path.join(root, name)
                lower = name.lower()

                if lower.endswith(".lang"):
                    self._check_lang(path)
                elif lower.endswith(".json") and lower not in [
                    "manifest.json",
                    "languages.json",
                    "pack_icon.json",
                    "contents.json",
                    "world_behavior_packs.json",
                    "world_resource_packs.json",
                ]:
                    self._check_json(path)

        return self.issues

    def _check_lang(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                raw = line.strip()
                if not raw or raw.startswith("#") or "=" not in raw:
                    continue

                key, value = raw.split("=", 1)
                if self._looks_untranslated(value):
                    self.issues.append({
                        "file": path,
                        "line": i,
                        "key": key,
                        "text": value,
                        "type": "lang",
                    })
        except Exception:
            pass

    def _check_json(self, path):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            self._walk_json(data, path)
        except Exception:
            pass

    def _walk_json(self, obj, path, key_path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                next_key = f"{key_path}.{k}" if key_path else str(k)
                self._walk_json(v, path, next_key)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                self._walk_json(v, path, f"{key_path}[{i}]")
        elif isinstance(obj, str) and self._looks_untranslated(obj):
            self.issues.append({
                "file": path,
                "line": "-",
                "key": key_path,
                "text": obj,
                "type": "json",
            })

    def _looks_untranslated(self, text):
        if not text:
            return False

        cleaned = re.sub(r"§.", "", str(text))
        cleaned = cleaned.replace("\\n", " ")
        cleaned = re.sub(r"%\d*\$?[sd]", "", cleaned)

        if re.search(r"[ぁ-んァ-ン一-龥]", cleaned):
            return False

        # IDs, paths, namespaces, and placeholders are not treated as untranslated prose.
        if re.fullmatch(r"[a-z0-9_:\-./]+", cleaned.strip(), re.I):
            if " " not in cleaned.strip():
                return False

        english_words = re.findall(r"[A-Za-z]{3,}", cleaned)
        return len(english_words) >= 1
