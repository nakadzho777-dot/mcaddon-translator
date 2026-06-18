import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY が設定されていません")

api_key = api_key.strip()
client = OpenAI(api_key=api_key)

BASE_URL = "https://mcaddon-translator-production.up.railway.app"
OUTPUT_DIR = "landing/blog"

keywords = [
    "mcaddon 翻訳 方法",
    "minecraft addon translate 方法",
    "マイクラ アドオン 日本語化 方法",
    "mcpack 翻訳 方法",
    "minecraft json 翻訳 方法",
]

def slugify(text):
    return text.lower().replace(" ", "-")

def generate_content(keyword):
    prompt = f"""あなたはプロのSEOライターです。

「{keyword}」というキーワードで記事を書いてください。
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content

def generate_article(keyword):
    slug = slugify(keyword)
    filename = f"{slug}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)

    print(f"生成中: {keyword}")

    content = generate_content(keyword)

    html = f"""<html><body>
<h1>{keyword}</h1>
{content}
</body></html>
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filename

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for kw in keywords:
        generate_article(kw)

    print("完了")

if __name__ == "__main__":
    main()
