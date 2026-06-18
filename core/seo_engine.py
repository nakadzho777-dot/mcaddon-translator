import json
import re

from core.llm_client import chat


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return None


def generate_seo(keyword: str) -> dict:
    prompt = f"""
次のキーワードでSEOメタ情報をJSONだけで出力してください。

キーワード:
{keyword}

形式:
{{
  "title": "...",
  "description": "...",
  "slug": "..."
}}

条件:
- titleは32〜55文字
- descriptionは80〜120文字
- slugは英数字・日本語・ハイフンのみ
"""

    result = chat(prompt)
    data = extract_json(result)

    if not data:
        data = {
            "title": f"【2026年最新版】{keyword}を初心者向けに解説",
            "description": f"{keyword}について、初心者にも分かりやすく手順と注意点を解説します。",
            "slug": slugify(keyword),
        }

    data["title"] = data.get("title") or f"【2026年最新版】{keyword}"
    data["description"] = data.get("description") or keyword
    data["slug"] = slugify(data.get("slug") or keyword)

    return data


def generate_article_body(keyword: str) -> str:
    prompt = f"""
あなたはMinecraft統合版アドオンに詳しいSEOライターです。

次のキーワードで日本語SEO記事を書いてください。

キーワード:
{keyword}

条件:
- 2500〜4000文字
- 初心者向け
- h2/h3見出しを使う
- 具体的な手順を入れる
- よくあるエラーと対処法を入れる
- 最後に翻訳ツールへの導線を自然に入れる
- 過度な誇張は禁止
"""

    return chat(prompt)


def score_article(keyword: str, title: str, body: str) -> int:
    prompt = f"""
次の記事をSEO観点で0〜100点で採点してください。
数字だけ返してください。

キーワード:
{keyword}

タイトル:
{title}

本文冒頭:
{body[:1500]}
"""

    try:
        result = chat(prompt)
        match = re.search(r"\d+", result)
        if match:
            score = int(match.group())
            return max(0, min(score, 100))
    except Exception:
        pass

    return 70


def rewrite_if_needed(keyword: str, title: str, body: str, score: int) -> str:
    if score >= 70:
        return body

    prompt = f"""
次の記事はSEOスコアが低いです。改善版を作成してください。

キーワード:
{keyword}

タイトル:
{title}

現在スコア:
{score}

本文:
{body}

改善条件:
- 検索意図により近づける
- 見出しを整理する
- 手順を分かりやすくする
- 具体例を追加する
- 初心者向けにする
"""

    return chat(prompt, timeout=180)