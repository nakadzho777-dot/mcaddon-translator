import os
import json
import time
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    import argostranslate.package
    import argostranslate.translate
except Exception:
    argostranslate = None


class AIEngine:
    def __init__(self):
        self._reload_settings()

    def _reload_settings(self):
        if load_dotenv:
            # override=True にして、設定画面で .env を更新した後も反映しやすくする
            try:
                load_dotenv(override=True)
            except TypeError:
                load_dotenv()

        config = self._load_config()

        self.engine = str(
            os.getenv("TRANSLATE_ENGINE")
            or config.get("engine")
            or "argos"
        ).strip().lower()

        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.openrouter_model = str(
            os.getenv("OPENROUTER_MODEL")
            or config.get("openrouter_model")
            or "openai/gpt-4o-mini"
        ).strip()

        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = str(
            os.getenv("OPENAI_MODEL")
            or config.get("model")
            or "gpt-4o-mini"
        ).strip()

        self.ollama_model = str(
            os.getenv("OLLAMA_MODEL")
            or config.get("ollama_model")
            or "gemma3"
        ).strip()

        self.site_url = os.getenv("SITE_URL", "https://mcaddon-translator.local").strip()

    def _load_config(self):
        path = os.path.join("data", "config.json")
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def translate(self, text: str):
        results = self.translate_batch([text])
        return results[0] if results else text

    def translate_batch(self, texts):
        if not texts:
            return []

        self._reload_settings()
        texts = ["" if t is None else str(t) for t in texts]

        if self.engine == "argos":
            return self._translate_argos(texts)

        if self.engine == "ollama":
            return self._translate_ollama_batch(texts)

        if self.engine == "openrouter":
            return self._translate_openrouter_batch(texts)

        if self.engine == "openai":
            return self._translate_openai_batch(texts)

        return [f"[ERROR] Unknown engine: {self.engine}" for _ in texts]

    def _translate_argos(self, texts):
        if argostranslate is None:
            return [f"[OFFLINE] Argos Translate is not installed: {t}" for t in texts]

        results = []
        for text in texts:
            try:
                translated = argostranslate.translate.translate(text, "en", "ja")
                results.append(translated)
            except Exception as e:
                results.append(f"[ERROR] Argos: {e}")
        return results

    def _translate_ollama_batch(self, texts):
        payload = {
            "model": self.ollama_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional Japanese translator for Minecraft Bedrock addons. "
                        "Translate each input string into natural Japanese. "
                        "Preserve Minecraft formatting codes such as §a, §r, \\n, %s, %1$s. "
                        "Return only a valid JSON array of strings. Do not return markdown."
                    )
                },
                {"role": "user", "content": json.dumps(texts, ensure_ascii=False)}
            ],
            "stream": False,
            "temperature": 0.1
        }
        return self._request_with_retries(
            url="http://127.0.0.1:11434/api/chat",
            payload=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            texts=texts,
            parser=lambda body: self._parse_ollama_response(body, len(texts)),
            paid_service=False,
        )

    def _translate_openrouter_batch(self, texts):
        if not self.openrouter_key:
            return [f"[OFFLINE] OpenRouter API key is not set: {t}" for t in texts]

        payload = self._chat_payload(self.openrouter_model, texts)
        return self._request_with_retries(
            url="https://openrouter.ai/api/v1/chat/completions",
            payload=payload,
            headers={
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json; charset=utf-8",
                "HTTP-Referer": self._ascii_safe(self.site_url),
                "X-Title": "MCAddon Translator",
            },
            texts=texts,
            parser=lambda body: self._parse_openai_style_response(body, len(texts)),
            paid_service=True,
        )

    def _translate_openai_batch(self, texts):
        if not self.openai_key:
            return [f"[OFFLINE] OpenAI API key is not set: {t}" for t in texts]

        payload = self._chat_payload(self.openai_model, texts)
        return self._request_with_retries(
            url="https://api.openai.com/v1/chat/completions",
            payload=payload,
            headers={
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json; charset=utf-8",
            },
            texts=texts,
            parser=lambda body: self._parse_openai_style_response(body, len(texts)),
            paid_service=True,
        )

    def _chat_payload(self, model, texts):
        return {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional Japanese translator for Minecraft Bedrock addons. "
                        "Translate each input string into natural Japanese. "
                        "Preserve Minecraft formatting codes such as §a, §r, \\n, %s, %1$s. "
                        "Return only a valid JSON array of strings. "
                        "The array length must match the input length. Do not return markdown."
                    )
                },
                {"role": "user", "content": json.dumps(texts, ensure_ascii=False)}
            ],
            "temperature": 0.1,
        }

    def _request_with_retries(self, url, payload, headers, texts, parser, paid_service=False):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        last_error = None

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=data, method="POST", headers=headers)
                with urllib.request.urlopen(req, timeout=120) as response:
                    body = response.read().decode("utf-8", errors="replace")

                parsed = parser(body)
                if isinstance(parsed, list) and len(parsed) == len(texts):
                    return [str(x) for x in parsed]

                last_error = "AI returned invalid JSON array length"

            except urllib.error.HTTPError as e:
                detail = ""
                try:
                    detail = e.read().decode("utf-8", errors="replace")
                except Exception:
                    detail = str(e)

                if e.code == 402:
                    return ["[ERROR] HTTPError: HTTP Error 402: Payment Required" for _ in texts]
                if e.code in (401, 403):
                    return [f"[ERROR] HTTPError: HTTP Error {e.code}: API key or permission error" for _ in texts]
                if e.code == 429:
                    last_error = "HTTPError: HTTP Error 429: Rate limit"
                else:
                    last_error = f"HTTPError: HTTP Error {e.code}: {detail[:300]}"

            except urllib.error.URLError as e:
                last_error = f"URLError: {e}"

            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"

            time.sleep(2 + attempt * 2)

        return [f"[ERROR] {last_error}" for _ in texts]

    def _parse_openai_style_response(self, body, expected_count):
        result = json.loads(body)
        content = result["choices"][0]["message"]["content"].strip()
        return self._parse_json_array(content, expected_count)

    def _parse_ollama_response(self, body, expected_count):
        result = json.loads(body)
        content = result.get("message", {}).get("content", "").strip()
        return self._parse_json_array(content, expected_count)

    def _parse_json_array(self, content, expected_count=None):
        content = str(content).strip()
        if content.startswith("```"):
            content = content.strip("`")
            content = content.replace("json\n", "", 1).replace("JSON\n", "", 1).strip()

        start = content.find("[")
        end = content.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return []

        data = json.loads(content[start:end + 1])
        if not isinstance(data, list):
            return []
        if expected_count is not None and len(data) != expected_count:
            return []
        return data

    def _ascii_safe(self, text):
        try:
            text.encode("ascii")
            return text
        except Exception:
            return "https://mcaddon-translator.local"
