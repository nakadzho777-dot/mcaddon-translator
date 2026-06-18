import time
from collections import defaultdict

from core.logger import log_event


# =========================
# ブロックリスト
# =========================
blocked_ips = set()


# =========================
# リクエスト履歴
# =========================
request_history = defaultdict(list)


# =========================
# IPブロック
# =========================
def block_ip(ip: str, reason: str = ""):
    blocked_ips.add(ip)
    log_event(f"IP_BLOCKED {ip} {reason}")


def is_blocked(ip: str):
    return ip in blocked_ips


# =========================
# 異常検知
# =========================
def detect_abuse(ip: str):
    now = time.time()

    request_history[ip] = [
        t for t in request_history[ip]
        if now - t < 10
    ]

    request_history[ip].append(now)

    if len(request_history[ip]) > 20:
        block_ip(ip, "rate_abuse")
        return True

    return False


# =========================
# APIキー検証（簡易版）
# =========================
VALID_KEYS = {"demo-key-123", "admin-key-999"}


def verify_api_key(key: str):
    if key not in VALID_KEYS:
        log_event("INVALID_API_KEY", level="WARNING")
        return False

    return True


# =========================
# セキュアガード
# =========================
def security_guard(ip: str, api_key: str):
    if is_blocked(ip):
        return {
            "status": "blocked",
            "reason": "ip_blocked"
        }

    if not verify_api_key(api_key):
        return {
            "status": "denied",
            "reason": "invalid_api_key"
        }

    if detect_abuse(ip):
        return {
            "status": "blocked",
            "reason": "abuse_detected"
        }

    return {"status": "ok"}