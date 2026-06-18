import time
import requests

from core.logger import log_event


# =========================
# APIリクエスト統一レイヤー
# =========================
def request(url: str, method: str = "GET", headers=None, data=None, retries: int = 2):
    headers = headers or {}

    for attempt in range(retries + 1):
        try:
            log_event(f"API_CALL {method} {url} attempt={attempt+1}")

            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)

            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)

            else:
                raise ValueError("Unsupported method")

            if response.status_code >= 400:
                raise Exception(f"HTTP {response.status_code}")

            return response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text

        except Exception as e:
            log_event(f"API_ERROR {url} {e}", level="WARNING")

            time.sleep(2)

    log_event(f"API_FAILED {url}", level="ERROR")

    return None


# =========================
# OpenAIラッパー例
# =========================
def call_openai(client, messages, model="gpt-4o-mini"):
    try:
        log_event("OPENAI_REQUEST")

        res = client.chat.completions.create(
            model=model,
            messages=messages
        )

        return res.choices[0].message.content

    except Exception as e:
        log_event(f"OPENAI_ERROR {e}", level="ERROR")
        return None


# =========================
# Stripe統一呼び出し例
# =========================
def call_stripe(endpoint: str, api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    return request(f"https://api.stripe.com/{endpoint}", headers=headers)


# =========================
# 外部サービスヘルスチェック
# =========================
def check_service(url: str):
    result = request(url)

    return {
        "url": url,
        "status": "ok" if result else "fail"
    }