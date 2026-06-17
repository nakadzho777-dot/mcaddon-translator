from core.cache import Cache
from core.mc_dictionary import MCDictionary
from core.ai_engine import AIEngine


class Translator:

    def __init__(self):

        self.cache = Cache()
        self.mc_dict = MCDictionary()
        self.ai = AIEngine()

    # =========================
    # メイン翻訳
    # =========================
    def translate(self, text: str):

        if not text:
            return ""

        # -------------------------
        # ① キャッシュ確認
        # -------------------------
        cached = self.cache.get(text)
        if cached:
            return cached

        # -------------------------
        # ② Minecraft辞書チェック
        # -------------------------
        mc_result = self.mc_translate(text)
        if mc_result:
            self.cache.set(text, mc_result)
            return mc_result

        # -------------------------
        # ③ AI翻訳
        # -------------------------
        ai_result = self.ai.translate(text)

        # -------------------------
        # ④ キャッシュ保存
        # -------------------------
        self.cache.set(text, ai_result)

        return ai_result

    # =========================
    # Minecraft専用翻訳
    # =========================
    def mc_translate(self, text: str):

        words = text.split()
        translated = []

        found = False

        for w in words:

            t = self.mc_dict.get(w)

            if t:
                translated.append(t)
                found = True
            else:
                translated.append(w)

        if found:
            return " ".join(translated)

        return None