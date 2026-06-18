import os
import re
from collections import defaultdict

BLOG_DIR = "landing/blog"

def extract_keywords(text):
    # 超簡易キーワード抽出
    words = re.findall(r"[a-zA-Z一-龥ぁ-んァ-ン]+", text)
    return list(set(words))


def build_index():
    index = {}

    for file in os.listdir(BLOG_DIR):
        if not file.endswith(".html"):
            continue

        path = os.path.join(BLOG_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        index[file] = {
            "content": content,
            "keywords": extract_keywords(content)
        }

    return index


def add_internal_links(index):
    files = list(index.keys())

    for file in files:
        content = index[file]["content"]

        for target in files:
            if target == file:
                continue

            target_name = target.replace(".html", "")
            url = f"/blog/{target}"

            # キーワード一致でリンク化
            for kw in index[target]["keywords"][:5]:
                if kw in content:
                    link = f'<a href="{url}">{kw}</a>'
                    content = content.replace(kw, link, 1)

        index[file]["content"] = content

    return index


def write_back(index):
    for file, data in index.items():
        path = os.path.join(BLOG_DIR, file)

        with open(path, "w", encoding="utf-8") as f:
            f.write(data["content"])


def run_internal_linking():
    index = build_index()
    index = add_internal_links(index)
    write_back(index)

    print("✅ 内部リンク生成 完了")