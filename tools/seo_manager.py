import os
import json

OUTPUT_DIR = "landing/blog"
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.json")

KEYWORDS = [
    "minecraft アドオン 翻訳",
    "minecraft addon 日本語化",
    "mcaddon 変換 方法",
    "minecraft mod 翻訳",
    "minecraft addon 作り方",
    "minecraft addon エラー 修正",
    "mcaddon 解凍 方法",
    "minecraft addon 配布 方法",
    "minecraft addon テクスチャ編集",
    "minecraft addon 自動化"
]

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>

<body style="font-family:Arial; background:#0f172a; color:white; padding:40px;">

<h1>{title}</h1>

<p>Minecraftアドオンの作業は複雑ですが、自動化できます。</p>

<h2>解決策</h2>
<p>MCAddon Translator SaaSを使うことで効率化できます。</p>

<ul>
<li>自動翻訳</li>
<li>ファイル変換</li>
<li>一括処理</li>
</ul>

<h2>今すぐ試す</h2>
<a href="/" style="color:#60a5fa;">無料で使う</a>

</body>
</html>
"""

def slugify(text):
    return text.replace(" ", "-").replace("　", "-")


def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_index(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    index = load_index()

    for kw in KEYWORDS:
        slug = slugify(kw)
        filename = f"{slug}.html"
        path = os.path.join(OUTPUT_DIR, filename)

        # 重複チェック
        if filename in index:
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(title=kw))

        index.append(filename)
        print("generated:", filename)

    save_index(index)
    print("done. total:", len(index))


if __name__ == "__main__":
    generate()