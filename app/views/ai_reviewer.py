import json
import os
import re
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


class AIReviewer:
    def __init__(self):
        if load_dotenv:
            try:
                load_dotenv(override=True)
            except TypeError:
                load_dotenv()
        self.engine = os.getenv("TRANSLATE_ENGINE", "argos").strip().lower()
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma3").strip()

    def review_history(self, history, limit=40):
        pairs = []
        for item in history[-limit:]:
            source = str(item.get("source", "")).strip()
            result = str(item.get("result", "")).strip()
            if source and result:
                pairs.append({"source": source, "result": result})

        if not pairs:
            return []

        ai_reviews = self._review_with_ai(pairs)
        if ai_reviews:
            return ai_reviews

        return [self._rule_review(x["source"], x["result"]) for x in pairs]

    def _review_with_ai(self, pairs):
        prompt = (
            "You are reviewing Japanese translations for Minecraft Bedrock addon texts. "
            "For each pair, return JSON array items with: score, source, result, suggestion, reason. "
            "Score is 0-100. Suggestions should be natural Japanese. Preserve Minecraft formatting codes like §a, §r, \\n. "
            "Return only valid JSON array.\n\n"
            + json.dumps(pairs, ensure_ascii=False)
        )

        try:
            if self.engine == "openrouter" and self.openrouter_key:
                return self._chat_openai_style(
                    "https://openrouter.ai/api/v1/chat/completions",
                    self.openrouter_model,
                    self.openrouter_key,
                    prompt,
                    extra_headers={
                        "HTTP-Referer": os.getenv("SITE_URL", "https://mcaddon-translator.local"),
                        "X-Title": "MCAddon Translator",
                    },
                )

            if self.engine == "openai" and self.openai_key:
                return self._chat_openai_style(
                    "https://api.openai.com/v1/chat/completions",
                    self.openai_model,
                    self.openai_key,
                    prompt,
                )

            if self.engine == "ollama":
                return self._chat_ollama(prompt)
        except Exception:
            return []

        return []

    def _chat_openai_style(self, url, model, api_key, prompt, extra_headers=None):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        }
        if extra_headers:
            headers.update(extra_headers)

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        body = self._post_json(url, payload, headers)
        data = json.loads(body)
        content = data["choices"][0]["message"]["content"]
        return self._parse_reviews(content)

    def _chat_ollama(self, prompt):
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        body = self._post_json(
            "http://127.0.0.1:11434/api/chat",
            payload,
            {"Content-Type": "application/json; charset=utf-8"},
        )
        data = json.loads(body)
        return self._parse_reviews(data.get("message", {}).get("content", ""))

    def _post_json(self, url, payload, headers):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST", headers=headers)
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.read().decode("utf-8", errors="replace")

    def _parse_reviews(self, text):
        text = str(text).strip()
        if text.startswith("```"):
            text = text.strip("`").replace("json\n", "", 1).replace("JSON\n", "", 1).strip()
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1:
            return []
        data = json.loads(text[start:end + 1])
        if not isinstance(data, list):
            return []
        reviews = []
        for item in data:
            if not isinstance(item, dict):
                continue
            reviews.append({
                "score": str(item.get("score", "")),
                "source": str(item.get("source", "")),
                "result": str(item.get("result", "")),
                "suggestion": str(item.get("suggestion", "")),
                "reason": str(item.get("reason", "")),
                "engine": "ai",
            })
        return reviews

    def _rule_review(self, source, result):
        score = 90
        suggestion = result
        reasons = []

        if self._has_english(result):
            score -= 25
            reasons.append("翻訳文に英語が残っている可能性があります。")

        if self._lost_format_codes(source, result):
            score -= 25
            reasons.append("Minecraftの装飾コード（§など）が消えている可能性があります。")

        if len(result) > max(35, len(source) * 2):
            score -= 10
            reasons.append("アイテム名として長すぎる可能性があります。")

        if not re.search(r"[ぁ-んァ-ン一-龥]", result):
            score -= 20
            reasons.append("日本語が含まれていません。")

        score = max(0, min(100, score))
        if not reasons:
            reasons.append("大きな問題は見つかりませんでした。")

        return {
            "score": str(score),
            "source": source,
            "result": result,
            "suggestion": suggestion,
            "reason": " / ".join(reasons),
            "engine": "rule",
        }

    def _has_english(self, text):
        cleaned = re.sub(r"§.", "", text)
        words = re.findall(r"[A-Za-z]{4,}", cleaned)
        allowed = {"minecraft", "item", "block", "entity"}
        return any(w.lower() not in allowed for w in words)

    def _lost_format_codes(self, source, result):
        src_codes = re.findall(r"§.", source)
        if not src_codes:
            return False
        return any(code not in result for code in src_codes)
