import os
import sys
import json
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from core.llm_client import chat


OUTPUT_PATH = "data/keywords.json"

SEED_KEYWORDS = [
    "mcaddon 翻訳",
    "mcaddon 日本語化",
    "mcpack 翻訳",
    "minecraft addon 日本語化",
    "minecraft 統合版 アドオン 翻訳",
]


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def extract_json_array(text: str):
    try:
        match = re.search(r"\[.*\]", text, re.S)
        if match:
            data = json.loads(match.group())
            if isinstance(data, list):
                return [str(x).strip() for x in data if str(x).strip()]
    except Exception:
        pass

    return []


def generate_related_keywords(seed: str, count: int = 20):
    prompt = f"""
あなたはSEOキーワード設計の専門家です。

次の親キーワードから、検索流入が狙える関連キーワードを{count}個作成してください。

親キーワード:
{seed}

条件:
- Minecraft統合版アドオン翻訳に関連する
- 初心者が検索しそうな語句
- 「やり方」「方法」「できない」「エラー」「日本語化」「lang」「json」などを含める
- 重複なし
- JSON配列だけで出力

例:
[
  "mcaddon 翻訳 やり方",
  "mcaddon 日本語化 方法"
]
"""

    result = chat(prompt)
    return extract_json_array(result)


def main():
    print("🚀 キーワード自動生成開始")

    all_keywords = []

    for seed in SEED_KEYWORDS:
        print(f"🔍 生成中: {seed}")

        try:
            keywords = generate_related_keywords(seed)
            all_keywords.extend(keywords)

        except Exception as e:
            print(f"❌ エラー: {seed}")
            print("詳細:", repr(e))

    unique_keywords = []

    for kw in all_keywords:
        if kw not in unique_keywords:
            unique_keywords.append(kw)

    ensure_dir(os.path.dirname(OUTPUT_PATH))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(unique_keywords, f, ensure_ascii=False, indent=2)

    print(f"✅ キーワード生成完了: {len(unique_keywords)}件")
    print(f"📄 保存先: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()