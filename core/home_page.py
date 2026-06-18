import os

LANDING_DIR = "landing"


def generate_home_page():
    os.makedirs(LANDING_DIR, exist_ok=True)

    html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>MCAddon Translator | Minecraft統合版アドオン翻訳ツール</title>
<meta name="description" content="MCAddon TranslatorはMinecraft統合版のmcaddon、mcpack、lang、json翻訳を効率化するツールです。">
<meta name="robots" content="index,follow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<h1>MCAddon Translator</h1>

<p>
Minecraft統合版アドオンの日本語化を効率化する翻訳ツールです。
mcaddon / mcpack / lang / json の翻訳作業をサポートします。
</p>

<section>
<h2>できること</h2>
<ul>
<li>mcaddon / mcpack の翻訳補助</li>
<li>langファイルの日本語化</li>
<li>json内テキストの抽出と翻訳</li>
<li>翻訳記事による使い方解説</li>
</ul>
</section>

<section>
<h2>まず試す</h2>
<p><a href="/pricing">料金プランを見る</a></p>
<p><a href="/blog/">使い方ブログを見る</a></p>
<p><a href="https://github.com/nakadzho777-dot/mcaddon-translator">GitHubを見る</a></p>
</section>

<section>
<h2>おすすめ記事</h2>
<ul>
<li><a href="/blog/mcaddon-翻訳-やり方.html">mcaddon 翻訳 やり方</a></li>
<li><a href="/blog/mcaddon-nihongo-ka-houhou.html">mcaddon 日本語化 方法</a></li>
<li><a href="/blog/minecraft-addon-nihongo.html">minecraft addon 日本語にする方法</a></li>
</ul>
</section>

</body>
</html>
"""

    with open(os.path.join(LANDING_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ home page 生成完了")