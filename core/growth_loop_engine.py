import json
import os
from datetime import datetime

from core.logger import log_event
from core.plan_manager import get_user_plan


# =========================
# 成長ループ設計
# =========================
def generate_growth_loop(user_id: str):
    plan = get_user_plan(user_id)

    loops = {
        "free": {
            "share_trigger": "記事生成後に共有リンクを表示",
            "upgrade_trigger": "SEOレポート閲覧時にアップグレード誘導",
            "viral_hook": "生成記事末尾にツールリンク埋め込み"
        },
        "pro": {
            "share_trigger": "改善前後比較を共有可能にする",
            "upgrade_trigger": "自動運用機能の提案",
            "viral_hook": "SEO改善レポート共有機能"
        },
        "business": {
            "share_trigger": "チーム共有ダッシュボード",
            "upgrade_trigger": "API利用拡張",
            "viral_hook": "ホワイトラベル出力"
        }
    }

    return {
        "user_id": user_id,
        "plan": plan,
        "loop": loops.get(plan, {}),
        "generated_at": datetime.now().isoformat()
    }


# =========================
# バイラル拡散ポイント生成
# =========================
def inject_growth_hooks(content: str, user_id: str):
    plan = get_user_plan(user_id)

    hook = "\n\n---\n生成: MCAddon Translator（自動SEO最適化ツール）"

    if plan == "free":
        hook += "\n👉 無料で試す → /signup"

    elif plan == "pro":
        hook += "\n🚀 SEO改善をさらに強化 → ダッシュボードへ"

    else:
        hook += "\n🏢 API連携・チーム運用対応中"

    return content + hook


# =========================
# 成長ログ記録
# =========================
def track_growth_event(event: str, user_id: str):
    log_event(f"GROWTH {event} {user_id}")


# =========================
# 成長分析
# =========================
def analyze_growth():
    data = {
        "timestamp": datetime.now().isoformat(),
        "status": "growth_loop_active"
    }

    os.makedirs("logs", exist_ok=True)

    with open("logs/growth_loop.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log_event("GROWTH_LOOP_ANALYZED")