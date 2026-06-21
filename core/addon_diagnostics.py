import os
import json
import re


class AddonDiagnostics:
    def __init__(self):
        self.report = []

    def run(self, root_path):
        self.report = []

        if not root_path or not os.path.exists(root_path):
            self._add("ERROR", "対象パスが見つかりません", "先にアドオンを翻訳または選択してください。")
            return self.report

        root = root_path if os.path.isdir(root_path) else os.path.dirname(root_path)

        self._check_manifest(root)
        self._check_texts(root)
        self._check_languages(root)
        self._check_japanese_files(root)
        self._check_json_syntax(root)
        self._check_empty_files(root)
        self._check_translation_rate(root)

        return self.report

    def _add(self, status, item, detail=""):
        self.report.append({
            "status": status,
            "item": item,
            "detail": detail,
        })

    def _find_files(self, root, filename_lower=None, suffix=None):
        found = []
        for r, _, files in os.walk(root):
            for name in files:
                lower = name.lower()
                if filename_lower and lower == filename_lower:
                    found.append(os.path.join(r, name))
                elif suffix and lower.endswith(suffix):
                    found.append(os.path.join(r, name))
        return found

    def _find_text_folders(self, root):
        folders = []
        for r, dirs, _ in os.walk(root):
            for d in dirs:
                if d.lower() == "texts":
                    folders.append(os.path.join(r, d))
        return folders

    def _check_manifest(self, root):
        manifests = self._find_files(root, filename_lower="manifest.json")
        if manifests:
            self._add("OK", "manifest.json", f"{len(manifests)} 個見つかりました。")
        else:
            self._add("ERROR", "manifest.json", "アドオンの基本情報ファイルが見つかりません。")

    def _check_texts(self, root):
        folders = self._find_text_folders(root)
        if folders:
            self._add("OK", "texts フォルダ", f"{len(folders)} 個見つかりました。")
        else:
            self._add("WARN", "texts フォルダ", "翻訳用 texts フォルダが見つかりません。JSON直書き型の可能性もあります。")

    def _check_languages(self, root):
        files = self._find_files(root, filename_lower="languages.json")
        if not files:
            self._add("WARN", "languages.json", "languages.json が見つかりません。ja_JP が読み込まれない可能性があります。")
            return

        ok_count = 0
        warn_count = 0
        for path in files:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                if isinstance(data, list) and any(str(x).lower() == "ja_jp" for x in data):
                    ok_count += 1
                else:
                    warn_count += 1
            except Exception:
                warn_count += 1

        if ok_count:
            self._add("OK", "languages.json", f"ja_JP を含む languages.json: {ok_count} 個")
        if warn_count:
            self._add("WARN", "languages.json", f"ja_JP が無い、または読み込めない languages.json: {warn_count} 個")

    def _check_japanese_files(self, root):
        ja_lang = self._find_files(root, filename_lower="ja_jp.lang")
        ja_json = self._find_files(root, filename_lower="ja_jp.json")

        if ja_lang or ja_json:
            self._add("OK", "日本語ファイル", f"ja_JP.lang: {len(ja_lang)} / ja_JP.json: {len(ja_json)}")
        else:
            self._add("WARN", "日本語ファイル", "ja_JP.lang / ja_JP.json が見つかりません。")

    def _check_json_syntax(self, root):
        error_count = 0
        checked = 0
        for path in self._find_files(root, suffix=".json"):
            checked += 1
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    json.load(f)
            except Exception as e:
                error_count += 1
                self._add("ERROR", "JSON構文エラー", f"{path} / {e}")

        if error_count == 0:
            self._add("OK", "JSON構文", f"{checked} 個のJSONを確認しました。")

    def _check_empty_files(self, root):
        empty = []
        for r, _, files in os.walk(root):
            for name in files:
                path = os.path.join(r, name)
                try:
                    if os.path.getsize(path) == 0:
                        empty.append(path)
                except Exception:
                    pass

        if empty:
            for path in empty[:30]:
                self._add("WARN", "空ファイル", path)
            if len(empty) > 30:
                self._add("WARN", "空ファイル", f"他 {len(empty) - 30} 件")
        else:
            self._add("OK", "空ファイル", "空ファイルは見つかりませんでした。")

    def _check_translation_rate(self, root):
        total = 0
        untranslated = 0

        for path in self._find_files(root, suffix=".lang"):
            name = os.path.basename(path).lower()
            if not name.startswith("ja_jp"):
                continue
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        _, value = line.split("=", 1)
                        total += 1
                        if self._looks_english(value):
                            untranslated += 1
            except Exception:
                pass

        for path in self._find_files(root, filename_lower="ja_jp.json"):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                strings = []
                self._collect_strings(data, strings)
                for value in strings:
                    total += 1
                    if self._looks_english(value):
                        untranslated += 1
            except Exception:
                pass

        if total == 0:
            self._add("INFO", "翻訳率", "日本語翻訳ファイル内の翻訳対象を確認できませんでした。")
            return

        rate = max(0, int(((total - untranslated) / total) * 100))
        status = "OK" if untranslated == 0 else "WARN"
        self._add(status, "翻訳率", f"{rate}% / 未翻訳らしき項目 {untranslated} 件 / 総項目 {total} 件")

    def _collect_strings(self, obj, out):
        if isinstance(obj, dict):
            for v in obj.values():
                self._collect_strings(v, out)
        elif isinstance(obj, list):
            for v in obj:
                self._collect_strings(v, out)
        elif isinstance(obj, str):
            out.append(obj)

    def _looks_english(self, text):
        cleaned = re.sub(r"§.", "", str(text))
        cleaned = cleaned.replace("\\n", " ")
        if re.search(r"[ぁ-んァ-ン一-龥]", cleaned):
            return False
        return bool(re.search(r"[A-Za-z]{3,}", cleaned))
