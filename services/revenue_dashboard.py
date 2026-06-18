import os
import json
from datetime import datetime
from collections import defaultdict

from core.logger import log_event

LOG_PATH = "logs/logs.json"
OUTPUT_PATH = "logs/revenue_dashboard.json"


# =========================
# ログ読み込み
# =========================
def load_logs():
    if not os.path.exists(LOG_PATH):
        return []

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


# =========================
# 収益シミュレーション
# =========================
def estimate_revenue(logs):
    revenue_map = defaultdict(int)
    user_map = defaultdict(int)

    for log in logs:
        event = log.get("event", "")
        level = log.get("level", "")

        # 記事生成＝価値行動
        if "API_GENERATE" in event:
            parts = event.split()
            if len(parts) >= 3:
                user = parts[1]
                keyword = " ".join(parts[2:])

                revenue_map[user] += 120  # 仮単価
                user_map[keyword] += 1

        if level == "ERROR":
            revenue_map["system_loss"] += 1

    return revenue_map, user_map


# =========================
# ダッシュボード生成
# =========================
def build_dashboard():
    logs = load_logs()

    revenue_map, keyword_map = estimate_revenue(logs)

    total_revenue = sum(revenue_map.values())

    top_users = sorted(
        revenue_map.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    top_keywords = sorted(
        keyword_map.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "total_estimated_revenue": total_revenue,
        "top_users": top_users,
        "top_keywords": top_keywords
    }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    log_event("REVENUE_DASHBOARD_UPDATED")

    print("💰 収益ダッシュボード更新完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    build_dashboard()