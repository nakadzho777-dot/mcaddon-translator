import os
import re
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.cta_builder import build_cta

BLOG_DIR = "landing/blog"


def remove_old_cta(html: str) -> str:
    html = re.sub(
        r'<section id="cta".*?</section>',
        "",
        html,
        flags=re.S
    )
    return html


def rebuild():
    if not os.path.exists(BLOG_DIR):
        print("❌ blog directory not found")
        return

    cta = build_cta()
    count = 0

    for filename in os.listdir(BLOG_DIR):
        if not filename.endswith(".html"):
            continue

        if filename == "index.html":
            continue

        path = os.path.join(BLOG_DIR, filename)

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        html = remove_old_cta(html)

        if "</article>" in html:
            html = html.replace("</article>", cta + "\n</article>")
        elif "</body>" in html:
            html = html.replace("</body>", cta + "\n</body>")
        else:
            html += cta

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        count += 1

    print(f"✅ CTA再注入完了: {count}記事")


if __name__ == "__main__":
    rebuild()