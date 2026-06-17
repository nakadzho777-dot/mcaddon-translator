import os

try:
    from openai import OpenAI
except:
    OpenAI = None


class AIEngine:

    def __init__(self):

        self.api_key = os.getenv("OPENAI_API_KEY")

        # APIキーがない場合でも起動可能にする
        if OpenAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False

    # =========================
    # 翻訳
    # =========================
    def translate(self, text: str):

        # AIなしモード
        if not self.enabled:
            return f"[OFFLINE] {text}"

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=f"Translate to Japanese (Minecraft context): {text}"
            )

            return response.output_text

        except Exception as e:
            return f"[ERROR] {str(e)}"