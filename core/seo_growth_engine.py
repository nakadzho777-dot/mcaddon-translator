import os
import json
from datetime import datetime
from openai import OpenAI

from core.logger import log_event

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RANKING_PATH = "logs/ranking.json"
OUTPUT_PATH = "logs/seo_growth.json"


# =========================
# ランキング読み込み
# =========================
def load_ranking():
    if not os.path.exists(RANKING_PATH):
        return None

    with open(RANKING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# SEO成長分析
# =========================
def analyze_growth(keyword, score):
    prompt = f"""
あなたはGoogle SEO戦略家です。

以下の情報から「検索順位を上げるための戦略」を出してください。

キーワード: {keyword}
スコア: {score}

出力:
- 今の弱点
- 上位表示するための改善
- CTR改善案
- 内部リンク戦略
- 優先度（High / Mid / Low）
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return res.choices[0].message.content


# =========================
# 成長レポート生成
# =========================
def build_growth_report():
    ranking = load_ranking()

    if not ranking:
        print("❌ rankingなし")
        return

    report = {}

    for keyword, data in ranking["ranking"]:
        score = data.get("score", 0)

        print(f"📈 成長分析: {keyword}")

        analysis = analyze_growth(keyword, score)

        report[keyword] = {
            "score": score,
            "growth_strategy": analysis
        }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    log_event("SEO_GROWTH_ENGINE_UPDATED")

    print("🚀 SEO成長エンジン完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    build_growth_report()