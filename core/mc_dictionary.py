class MCDictionary:

    def __init__(self):

        # Minecraft用基本辞書
        self.data = {
            "stone": "石",
            "dirt": "土",
            "sand": "砂",
            "diamond": "ダイヤモンド",
            "iron": "鉄",
            "gold": "金",
            "coal": "石炭",
            "wood": "木材",
            "log": "原木",
            "plank": "木材の板",
            "stick": "棒",
            "crafting": "クラフト",
            "inventory": "インベントリ",
            "pickaxe": "ツルハシ",
            "axe": "斧",
            "sword": "剣",
            "shield": "盾",
            "bow": "弓",
            "arrow": "矢"
        }

    # =========================
    # 翻訳取得
    # =========================
    def get(self, key: str):

        if not key:
            return None

        return self.data.get(key.lower())