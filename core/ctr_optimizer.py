import os
import json
import random
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LOG_PATH = "logs/dashboard.json"
OUTPUT_PATH = "logs/ctr_titles.json"


# =========================
# ダッシュボード読み込み
# =========================
def load_data():
    if not os.path.exists(LOG_PATH):
        return None

    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# タイトル改善AI
# =========================
def improve_title(keyword, base_title):
    prompt = f"""
あなたはSEO専門家です。

以下のタイトルを「クリック率が最大化する形」に改善してください。

条件:
- 32〜55文字
- 数字 or 最新感を入れる
- クリックしたくなる表現
- 誇張しすぎない

キーワード:
{keyword}

元タイトル:
{base_title}

改善タイトルだけ出力してください。
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return res.choices[0].message.content.strip()


# =========================
# CTR生成
# =========================
def generate_ctr_titles():
    data = load_data()
    if not data:
        print("❌ データなし")
        return

    top_keywords = data.get("top_keywords", [])

    results = {}

    for kw, _ in top_keywords:
        base = f"【2026年最新版】{kw}｜初心者でも簡単に解説"
        improved = improve_title(kw, base)

        results[kw] = {
            "base": base,
            "optimized": improved
        }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("📈 CTR改善タイトル生成完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    generate_ctr_titles()