import json
import os
import hashlib
from typing import Optional


class TranslationStore:
    """
    翻訳履歴 + 差分管理 + 永続キャッシュ
    """

    def __init__(self, path="translation_store.json"):
        self.path = path
        self.data = self._load()

    # ----------------------------
    # load
    # ----------------------------

    def _load(self):
        if not os.path.exists(self.path):
            return {}

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ----------------------------
    # save
    # ----------------------------

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # ----------------------------
    # hash生成
    # ----------------------------

    def _hash(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    # ----------------------------
    # 翻訳済みか判定
    # ----------------------------

    def get(self, text: str) -> Optional[str]:
        key = self._hash(text)
        return self.data.get(key, None)

    # ----------------------------
    # 保存
    # ----------------------------

    def set(self, text: str, translated: str):
        key = self._hash(text)

        self.data[key] = {
            "original": text,
            "translated": translated
        }

        self._save()

    # ----------------------------
    # 変更チェック
    # ----------------------------

    def is_same(self, text: str) -> bool:
        return self._hash(text) in self.data