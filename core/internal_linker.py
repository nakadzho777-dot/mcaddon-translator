import os
import re

BLOG_DIR = "landing/blog"


def get_html_files():
    if not os.path.exists(BLOG_DIR):
        return []
    return [f for f in os.listdir(BLOG_DIR) if f.endswith(".html")]


def get_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    return match.group(1).strip() if match else ""


def remove_old_related_block(html: str) -> str:
    return re.sub(
        r"\n<section id=\"related-posts\">.*?</section>\n",
        "\n",
        html,
        flags=re.S,
    )


def run_internal_linking():
    files = get_html_files()

    if not files:
        print("⚠ 内部リンク対象なし")
        return

    pages = []

    for file in files:
        path = os.path.join(BLOG_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        pages.append({
            "file": file,
            "title": get_title(html),
        })

    for page in pages:
        path = os.path.join(BLOG_DIR, page["file"])

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        html = remove_old_related_block(html)

        related = [
            p for p in pages
            if p["file"] != page["file"]
        ][:5]

        block = '\n<section id="related-posts">\n<h2>関連記事</h2>\n<ul>\n'

        for r in related:
            anchor = r["title"] or r["file"].replace(".html", "")
            block += f'<li><a href="/blog/{r["file"]}">{anchor}</a></li>\n'

        block += "</ul>\n</section>\n"

        html = html.replace("</body>", block + "</body>")

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    print("🔗 内部リンク最適化完了")