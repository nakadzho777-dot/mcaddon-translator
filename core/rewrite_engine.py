import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BLOG_DIR = "landing/blog"
RANKING_PATH = "logs/ranking.json"


# =========================
# ランキング読み込み
# =========================
def load_ranking():
    if not os.path.exists(RANKING_PATH):
        return None

    with open(RANKING_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return None


# =========================
# HTML読み込み
# =========================
def load_article(file_name):
    path = os.path.join(BLOG_DIR, file_name)

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# =========================
# AIリライト
# =========================
def rewrite_content(html, keyword):
    prompt = f"""
あなたはSEO専門家です。

以下のHTML記事を改善してください。

目的:
- 検索順位を上げる
- 読みやすさ向上
- 情報は削除しない
- 見出し最適化

キーワード:
{keyword}

記事:
{html}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return res.choices[0].message.content


# =========================
# 保存
# =========================
def save_article(file_name, content):
    path = os.path.join(BLOG_DIR, file_name)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# =========================
# リライト実行
# =========================
def run_rewrite():
    ranking = load_ranking()

    if not ranking:
        print("❌ rankingなし")
        return

    # 上位3記事だけリライト（重要）
    top_articles = ranking["ranking"][:3]

    for keyword, data in top_articles:
        file_name = f"{keyword}.html"

        print(f"🔁 リライト中: {keyword}")

        html = load_article(file_name)
        if not html:
            continue

        improved = rewrite_content(html, keyword)

        save_article(file_name, improved)

    print("✅ 自動リライト完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    run_rewrite()