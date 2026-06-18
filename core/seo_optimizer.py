import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RANKING_PATH = "logs/ranking.json"
OUTPUT_PATH = "logs/seo_report.json"


# =========================
# ランキング読み込み
# =========================
def load_ranking():
    if not os.path.exists(RANKING_PATH):
        return None

    with open(RANKING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# SEO評価AI
# =========================
def evaluate_seo(keyword, score):
    prompt = f"""
あなたはGoogle SEO専門家です。

以下の記事を評価してください。

キーワード: {keyword}
スコア: {score}

以下を出力:
- 改善ポイント
- タイトル改善案
- 見出し改善案
- 優先度（High / Mid / Low）
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return res.choices[0].message.content


# =========================
# SEOレポート生成
# =========================
def generate_seo_report():
    ranking = load_ranking()

    if not ranking:
        print("❌ rankingなし")
        return

    report = {}

    for keyword, data in ranking["ranking"]:
        score = data.get("score", 0)

        print(f"🔍 SEO分析: {keyword}")

        analysis = evaluate_seo(keyword, score)

        report[keyword] = {
            "score": score,
            "analysis": analysis
        }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("📊 SEO最適化レポート完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    generate_seo_report()