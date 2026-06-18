import os
import json
from collections import defaultdict
from datetime import datetime

LOG_JSON = "logs/logs.json"
OUTPUT_JSON = "logs/dashboard.json"


# =========================
# ログ読み込み
# =========================
def load_logs():
    if not os.path.exists(LOG_JSON):
        return []

    with open(LOG_JSON, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


# =========================
# 集計処理
# =========================
def analyze_logs(logs):
    stats = {
        "total_events": 0,
        "errors": 0,
        "success": 0,
        "keywords": defaultdict(int),
        "timeline": defaultdict(int),
    }

    for log in logs:
        stats["total_events"] += 1

        level = log.get("level", "INFO")
        event = log.get("event", "")
        time = log.get("time", "")[:10]

        stats["timeline"][time] += 1

        if level == "ERROR":
            stats["errors"] += 1
        elif level == "SUCCESS":
            stats["success"] += 1

        # キーワード抽出（記事生成系）
        if "START" in event:
            kw = event.replace("START", "").strip()
            stats["keywords"][kw] += 1

    return stats


# =========================
# ダッシュボード生成
# =========================
def build_dashboard(stats):
    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_events": stats["total_events"],
            "success": stats["success"],
            "errors": stats["errors"],
        },
        "top_keywords": sorted(
            stats["keywords"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:20],
        "timeline": dict(stats["timeline"])
    }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    print("📊 ダッシュボード更新完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    logs = load_logs()
    stats = analyze_logs(logs)
    build_dashboard(stats)