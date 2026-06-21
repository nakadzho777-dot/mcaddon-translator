import os
import json
import re


JP_RE = re.compile(r"[ぁ-んァ-ヶ一-龥]")
EN_RE = re.compile(r"[A-Za-z]{3,}")


class TranslationStats:
    """翻訳率をざっくり判定する軽量アナライザー。"""

    def analyze(self, root_path):
        target = self._resolve_root(root_path)
        total = 0
        translated = 0
        untranslated = 0
        files = 0

        if not target or not os.path.exists(target):
            return self._result(total, translated, untranslated, files)

        for root, _, names in os.walk(target):
            for name in names:
                path = os.path.join(root, name)
                lower = name.lower()

                if lower.endswith('.lang'):
                    t, tr, un = self._analyze_lang(path)
                elif lower.endswith('.json') and lower not in {'manifest.json', 'languages.json'}:
                    t, tr, un = self._analyze_json(path)
                else:
                    continue

                if t > 0:
                    files += 1
                total += t
                translated += tr
                untranslated += un

        return self._result(total, translated, untranslated, files)

    def _resolve_root(self, root_path):
        if not root_path:
            return None
        if os.path.isfile(root_path):
            return os.path.dirname(root_path)
        return root_path

    def _result(self, total, translated, untranslated, files):
        rate = round((translated / total) * 100, 1) if total else 0.0
        return {
            'files': files,
            'total': total,
            'translated': translated,
            'untranslated': untranslated,
            'rate': rate,
        }

    def _analyze_lang(self, path):
        total = translated = untranslated = 0
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    value = line.split('=', 1)[1]
                    total += 1
                    if self._is_translated(value):
                        translated += 1
                    else:
                        untranslated += 1
        except Exception:
            pass
        return total, translated, untranslated

    def _analyze_json(self, path):
        total = translated = untranslated = 0
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            for value in self._walk_strings(data):
                if not self._should_count(value):
                    continue
                total += 1
                if self._is_translated(value):
                    translated += 1
                else:
                    untranslated += 1
        except Exception:
            pass
        return total, translated, untranslated

    def _walk_strings(self, obj):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from self._walk_strings(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from self._walk_strings(v)
        elif isinstance(obj, str):
            yield obj

    def _should_count(self, text):
        text = str(text).strip()
        if not text:
            return False
        if text.startswith('minecraft:') or text.startswith('textures/'):
            return False
        if '/' in text and ' ' not in text:
            return False
        return bool(EN_RE.search(text) or JP_RE.search(text))

    def _is_translated(self, text):
        cleaned = re.sub(r'§.', '', str(text))
        cleaned = cleaned.replace('\\n', ' ')
        return bool(JP_RE.search(cleaned))
