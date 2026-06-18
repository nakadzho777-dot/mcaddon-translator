import os

KEYWORDS = [
    "minecraft アドオン 翻訳",
    "minecraft addon 日本語化",
    "mcaddon 変換 方法",
    "minecraft mod 翻訳ツール",
    "minecraft addon 作り方"
]

OUTPUT_DIR = "landing/blog"

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>

<body style="font-family:Arial; background:#0f172a; color:white; padding:40px;">

<h1>{title}</h1>

<p>
Minecraftアドオンの翻訳は非常に時間がかかります。
しかし、この問題は自動化できます。
</p>

<h2>解決策</h2>

<p>
MCAddon Translator SaaSを使うことで、
ワンクリックで翻訳できます。
</p>

<ul>
<li>自動翻訳</li>
<li>mcaddon変換</li>
<li>一括処理</li>
</ul>

<h2>使い方</h2>
<ol>
<li>アップロード</li>
<li>自動翻訳</li>
<li>ダウンロード</li>
</ol>

<h2>今すぐ試す</h2>

<a href="/" style="color:#60a5fa; font-size:20px;">
無料で使う
</a>

</body>
</html>
"""

def slugify(text):
    return text.replace(" ", "-").replace("　", "-")


def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for kw in KEYWORDS:
        filename = slugify(kw) + ".html"
        path = os.path.join(OUTPUT_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(title=kw))

        print("generated:", path)


if __name__ == "__main__":
    generate()