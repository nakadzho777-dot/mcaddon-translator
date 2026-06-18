import os
import json
from datetime import datetime

LOG_PATH = "logs/logs.json"
OUTPUT_PATH = "logs/ranking.json"


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
# 記事別スコアリング
# =========================
def build_scores(logs):
    scores = {}

    for log in logs:
        event = log.get("event", "")
        level = log.get("level", "INFO")

        # 記事生成系のみ対象
        if "START" in event:
            kw = event.replace("START", "").strip()

            if kw not in scores:
                scores[kw] = {
                    "views": 0,
                    "errors": 0,
                    "score": 0
                }

            scores[kw]["views"] += 1

        if level == "ERROR":
            for k in scores:
                scores[k]["errors"] += 1

    # スコア計算
    for k, v in scores.items():
        v["score"] = v["views"] * 10 - v["errors"] * 5

    return scores


# =========================
# ランキング生成
# =========================
def generate_ranking():
    logs = load_logs()
    scores = build_scores(logs)

    ranking = sorted(
        scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    result = {
        "generated_at": datetime.now().isoformat(),
        "ranking": ranking
    }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("🏆 人気記事ランキング生成完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    generate_ranking()