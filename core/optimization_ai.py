import os
import json
from datetime import datetime
from openai import OpenAI

from core.logger import log_event

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LOG_PATH = "logs/logs.json"
OUTPUT_PATH = "logs/optimization_plan.json"


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
# AI最適化分析
# =========================
def analyze_system(logs):
    prompt = f"""
あなたはSaaSプロダクトの最適化AIです。

以下のログから「システム改善案」を作ってください。

目的:
- 収益最大化
- CTR向上
- SEO改善
- ユーザー増加

ログ:
{json.dumps(logs[:50], ensure_ascii=False)}

出力:
- 問題点
- 改善案
- 優先順位（High / Mid / Low）
- 次に実行すべき3アクション
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return res.choices[0].message.content


# =========================
# 最適化プラン生成
# =========================
def generate_optimization_plan():
    logs = load_logs()

    print("🧠 システム最適化中...")

    analysis = analyze_system(logs)

    plan = {
        "generated_at": datetime.now().isoformat(),
        "analysis": analysis
    }

    os.makedirs("logs", exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    log_event("OPTIMIZATION_PLAN_CREATED")

    print("🚀 最適化プラン生成完了")


# =========================
# 実行
# =========================
if __name__ == "__main__":
    generate_optimization_plan()