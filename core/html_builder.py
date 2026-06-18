from datetime import datetime


def build_html(seo: dict, body: str, score: int = 0) -> str:
    now = datetime.now().strftime("%Y-%m-%d")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>{seo["title"]}</title>
<meta name="description" content="{seo["description"]}">
<meta name="robots" content="index,follow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<article>
<h1>{seo["title"]}</h1>

<p><small>更新日: {now}</small></p>
<p><small>SEOスコア: {score}/100</small></p>

{body}

<hr>

<section>
<h2>MCAddon Translatorを使う</h2>
<p>
Minecraft統合版アドオンの翻訳を効率化したい場合は、
MCAddon Translatorを使うことでlangファイルやJSON翻訳を自動化できます。
</p>
<p><a href="/">👉 翻訳ツールはこちら</a></p>
</section>

</article>

</body>
</html>
"""