
import os
import json
import shutil
import zipfile
import tempfile
from pathlib import Path

from core.job_manager import JobManager
from core.checkpoint import CheckpointManager
from core.logger import Logger


class MCAddonProcessor:
    def __init__(self):
        self.job_manager = JobManager(max_workers=4)
        self.checkpoint = CheckpointManager()
        self.logger = Logger()

        self.files = []
        self.source_path = None
        self.work_dir = None
        self.scan_root = None
        self.output_path = None
        self.is_archive = False

    def scan(self, root_path: str):
        self.files = []
        self.source_path = root_path
        self.work_dir = None
        self.scan_root = root_path
        self.output_path = None
        self.is_archive = False

        path = Path(root_path)

        if path.is_file():
            suffix = path.suffix.lower()

            if suffix in [".mcaddon", ".mcpack", ".zip"]:
                self.is_archive = True
                self.work_dir = tempfile.mkdtemp(prefix="mcaddon_translator_")
                self.scan_root = self.work_dir

                self._extract_archive(str(path), self.work_dir)

                stem = path.stem
                self.output_path = str(path.with_name(stem + "_ja" + suffix))
            else:
                return []

        targets = []

        for root, _, files in os.walk(self.scan_root):
            for filename in files:
                lower = filename.lower()
                full_path = os.path.join(root, filename)

                if self._is_lang_file(lower):
                    targets.append({"path": full_path, "type": "lang"})

                elif self._is_json_file(lower):
                    targets.append({"path": full_path, "type": "json"})

        self.files = targets
        return targets

    def run(self, translator, progress_callback=None):
        self.job_manager.queue.queue.clear()

        for item in self.files:
            self.job_manager.add_job(self._process_file, item, translator)

        if progress_callback:
            self.job_manager.set_progress_callback(progress_callback)

        result = self.job_manager.run()

        self._ensure_all_texts_folders()

        if self.is_archive and self.output_path and self.scan_root:
            self._create_archive(self.scan_root, self.output_path)

        return result

    def _is_lang_file(self, filename: str):
        if not filename.endswith(".lang"):
            return False

        blocked = [
            "ja_jp.lang",
            "ja_jp.lang.tmp",
            "zh_cn.lang",
            "ko_kr.lang"
        ]

        return filename not in blocked

    def _is_json_file(self, filename: str):
        if not filename.endswith(".json"):
            return False

        blocked_names = [
            "manifest.json",
            "pack_icon.json",
            "contents.json",
            "world_behavior_packs.json",
            "world_resource_packs.json",
            "languages.json"
        ]

        return filename not in blocked_names

    def _extract_archive(self, archive_path: str, output_dir: str):
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(output_dir)

        self._extract_nested_packs(output_dir)

    def _extract_nested_packs(self, root_dir: str):
        for root, _, files in os.walk(root_dir):
            for filename in files:
                lower = filename.lower()

                if not lower.endswith((".mcpack", ".zip")):
                    continue

                pack_path = os.path.join(root, filename)
                extract_dir = os.path.join(root, Path(filename).stem)

                try:
                    os.makedirs(extract_dir, exist_ok=True)

                    with zipfile.ZipFile(pack_path, "r") as z:
                        z.extractall(extract_dir)

                    os.remove(pack_path)

                except Exception as e:
                    self.logger.error(f"nested extract error {pack_path}: {e}")

    def _create_archive(self, source_dir: str, output_path: str):
        if os.path.exists(output_path):
            os.remove(output_path)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    arcname = os.path.relpath(file_path, source_dir)
                    z.write(file_path, arcname)

    def _process_file(self, item, translator):
        file_path = item.get("path")
        file_type = item.get("type")

        try:
            if file_type == "lang":
                return self._process_lang(file_path, translator)

            if file_type == "json":
                return self._process_json(file_path, translator)

            return {"file": file_path, "error": "unknown type"}

        except Exception as e:
            self.logger.error(str(e))
            return {"file": file_path, "error": str(e)}

    def _process_lang(self, file_path: str, translator):
        output_path = self._lang_output_path(file_path)

        pairs = []
        output_lines = []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line in lines:
            raw = line.rstrip("\n").rstrip("\r")

            if not raw.strip():
                output_lines.append(raw)
                continue

            if raw.strip().startswith("#"):
                output_lines.append(raw)
                continue

            if "=" not in raw:
                output_lines.append(raw)
                continue

            key, value = raw.split("=", 1)

            if not value.strip():
                output_lines.append(raw)
                continue

            pairs.append((len(output_lines), key, value))
            output_lines.append(raw)

        texts = [v for _, _, v in pairs]

        if texts:
            try:
                translated = translator.translate_batch_fast(texts)
            except Exception as e:
                self.logger.error(f"lang batch error {file_path}: {e}")
                translated = texts

            for (line_index, key, _), new_text in zip(pairs, translated):
                output_lines[line_index] = f"{key}={new_text}"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self._remove_case_conflict(output_path)

        with open(output_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(output_lines))

        self._ensure_languages_json(os.path.dirname(output_path))

        return {
            "file": file_path,
            "output": output_path,
            "changed": True
        }

    def _lang_output_path(self, file_path: str):
        folder = os.path.dirname(file_path)
        return os.path.join(folder, "ja_JP.lang")

    def _process_json(self, file_path: str, translator):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        strings = []
        positions = []

        self._collect_strings(data, positions, strings)

        if not strings:
            return {"file": file_path, "changed": False}

        try:
            translated = translator.translate_batch_fast(strings)
        except Exception as e:
            self.logger.error(f"json batch error {file_path}: {e}")
            translated = strings

        for path, new_text in zip(positions, translated):
            self._set_value(data, path, new_text)

        output_path = self._json_output_path(file_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self._remove_case_conflict(output_path)

        tmp = output_path + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        os.replace(tmp, output_path)

        if os.path.basename(os.path.dirname(output_path)).lower() == "texts":
            self._ensure_languages_json(os.path.dirname(output_path))

        return {
            "file": file_path,
            "output": output_path,
            "changed": True
        }

    def _json_output_path(self, file_path: str):
        folder = os.path.dirname(file_path)
        filename = os.path.basename(file_path).lower()
        parent = os.path.basename(folder).lower()

        localization_names = [
            "en_us.json",
            "en_us.lang.json",
            "en_gb.json",
            "en-us.json",
            "texts.json"
        ]

        if parent == "texts" and filename in localization_names:
            return os.path.join(folder, "ja_JP.json")

        if filename in localization_names:
            return os.path.join(folder, "ja_JP.json")

        return file_path

    def _remove_case_conflict(self, desired_path: str):
        folder = os.path.dirname(desired_path)
        desired_name = os.path.basename(desired_path)
        desired_lower = desired_name.lower()

        if not os.path.isdir(folder):
            return

        for filename in os.listdir(folder):
            if filename.lower() == desired_lower and filename != desired_name:
                old_path = os.path.join(folder, filename)
                tmp_path = os.path.join(folder, "__case_fix_tmp__")

                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

                    os.rename(old_path, tmp_path)
                    os.remove(tmp_path)
                except Exception:
                    try:
                        os.remove(old_path)
                    except Exception:
                        pass

    def _ensure_all_texts_folders(self):
        if not self.scan_root or not os.path.exists(self.scan_root):
            return

        for root, _, files in os.walk(self.scan_root):
            if os.path.basename(root).lower() != "texts":
                continue

            has_lang = any(f.lower() in ["en_us.lang", "ja_jp.lang"] for f in files)
            has_json = any(f.lower() in ["en_us.json", "ja_jp.json"] for f in files)

            if has_lang or has_json:
                self._ensure_languages_json(root)

    def _ensure_languages_json(self, texts_folder: str):
        if os.path.basename(texts_folder).lower() != "texts":
            return

        path = os.path.join(texts_folder, "languages.json")

        languages = []

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    languages = [str(x) for x in data]
            except Exception:
                languages = []

        lowered = [x.lower() for x in languages]

        if "en_us" not in lowered:
            languages.insert(0, "en_US")

        lowered = [x.lower() for x in languages]

        if "ja_jp" not in lowered:
            languages.append("ja_JP")
        else:
            languages = ["ja_JP" if x.lower() == "ja_jp" else x for x in languages]

        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(languages, f, ensure_ascii=False, indent=2)

    def _collect_strings(self, obj, positions, strings, path=None):
        if path is None:
            path = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                if self._skip_key(key):
                    continue

                self._collect_strings(value, positions, strings, path + [key])

        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                self._collect_strings(value, positions, strings, path + [i])

        elif isinstance(obj, str):
            if self._should_translate_string(obj):
                positions.append(path)
                strings.append(obj)

    def _skip_key(self, key):
        key = str(key).lower()

        skip_keywords = [
            "uuid",
            "version",
            "format_version",
            "identifier",
            "texture",
            "textures",
            "icon",
            "geometry",
            "material",
            "materials",
            "sound",
            "sounds",
            "animation",
            "animations",
            "controller",
            "render_controllers",
            "minecraft:"
        ]

        return any(word in key for word in skip_keywords)

    def _should_translate_string(self, text):
        text = text.strip()

        if not text:
            return False

        if len(text) <= 1:
            return False

        if text.startswith("minecraft:"):
            return False

        if text.startswith("@"):
            return False

        if "/" in text and " " not in text:
            return False

        if "\\" in text:
            return False

        if text.endswith((".png", ".jpg", ".jpeg", ".tga", ".ogg", ".json")):
            return False

        return True

    def _set_value(self, obj, path, value):
        current = obj

        for key in path[:-1]:
            current = current[key]

        current[path[-1]] = value

    def cleanup(self):
        if self.work_dir and os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir, ignore_errors=True)