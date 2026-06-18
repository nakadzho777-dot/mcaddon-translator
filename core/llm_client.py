import os
import time
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_env_file(path=".env"):
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


load_env_file()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY が設定されていません")


def chat(prompt: str, retries: int = 3, timeout: int = 120) -> str:
    last_error = None

    for i in range(retries):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mcaddon-translator-production.up.railway.app",
                    "X-Title": "MCAddon Translator",
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "temperature": 0.7,
                },
                timeout=timeout,
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            last_error = e
            print(f"⚠ AIリトライ {i + 1}/{retries}: {e}")
            time.sleep(2 * (i + 1))

    raise RuntimeError(f"AI生成に失敗しました: {last_error}")