from datetime import datetime
from core.cta_builder import build_cta


def build_html(seo: dict, body: str, score: int = 0) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    cta = build_cta()

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

{cta}

</article>

</body>
</html>
"""