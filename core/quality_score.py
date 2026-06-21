import os
import json
import re


class QualityScoreAnalyzer:
    """
    翻訳済みアドオンの品質スコアを計算します。

    見るもの:
    - .lang 内の日本語率
    - 英語が残っている行
    - JSON構文エラー
    - Minecraft ID/パスらしきものの翻訳事故候補
    """

    JAPANESE_RE = re.compile(r"[ぁ-んァ-ヶ一-龥]")
    ENGLISH_WORD_RE = re.compile(r"[A-Za-z]{3,}")

    RISK_PATTERNS = [
        "minecraft:",
        "textures/",
        "geometry.",
        "animation.",
        "controller.",
        "entity.",
        "item.",
        "block.",
        "render_controllers",
    ]

    def analyze(self, root_path):
        result = {
            "score": 100,
            "total_texts": 0,
            "japanese_texts": 0,
            "untranslated": [],
            "mixed": [],
            "json_errors": [],
            "risk_items": [],
        }

        if not root_path or not os.path.exists(root_path):
            result["score"] = 0
            return result

        base = os.path.dirname(root_path) if os.path.isfile(root_path) else root_path

        for root, _, files in os.walk(base):
            for name in files:
                path = os.path.join(root, name)
                lower = name.lower()

                if lower.endswith(".lang"):
                    self._check_lang(path, result)

                elif lower.endswith(".json"):
                    self._check_json(path, result)

        result["score"] = self._calculate_score(result)
        return result

    def _check_lang(self, path, result):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, start=1):
                raw = line.strip()

                if not raw or raw.startswith("#") or "=" not in raw:
                    continue

                key, value = raw.split("=", 1)
                value_clean = value.replace("\\n", " ")
                value_clean = re.sub(r"§.", "", value_clean)

                result["total_texts"] += 1

                has_jp = bool(self.JAPANESE_RE.search(value_clean))
                has_en = bool(self.ENGLISH_WORD_RE.search(value_clean))

                if has_jp:
                    result["japanese_texts"] += 1

                if not has_jp and has_en:
                    result["untranslated"].append({
                        "file": path,
                        "line": i,
                        "key": key,
                        "text": value
                    })

                elif has_jp and has_en:
                    result["mixed"].append({
                        "file": path,
                        "line": i,
                        "key": key,
                        "text": value
                    })

        except Exception:
            pass

    def _check_json(self, path, result):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            try:
                json.loads(text)
            except Exception as e:
                result["json_errors"].append({
                    "file": path,
                    "error": str(e)
                })

            for pattern in self.RISK_PATTERNS:
                if pattern in text:
                    # 危険パターンそのものは正常なIDでも出るので、まずは要確認扱い
                    result["risk_items"].append({
                        "file": path,
                        "issue": f"要確認パターン: {pattern}"
                    })

        except Exception:
            pass

    def _calculate_score(self, result):
        score = 100

        total = result.get("total_texts", 0)
        jp = result.get("japanese_texts", 0)

        if total > 0:
            jp_rate = jp / total
            if jp_rate < 0.95:
                score -= int((0.95 - jp_rate) * 50)
        else:
            score -= 10

        score -= min(len(result["untranslated"]) * 2, 30)
        score -= min(len(result["mixed"]), 15)
        score -= min(len(result["json_errors"]) * 10, 40)
        score -= min(len(result["risk_items"]) // 5, 10)

        return max(0, min(100, score))
