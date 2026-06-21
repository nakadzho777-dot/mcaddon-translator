import tkinter as tk
from tkinter import ttk, messagebox


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#9bef28"
GOLD = "#facc15"


class ProUpgradeView:
    def __init__(
        self,
        parent,
        on_log=None,
        style_prefix="Free"
    ):
        self.parent = parent
        self.on_log = on_log
        self.style_prefix = style_prefix

    def open(self, feature_name="PRO機能"):
        win = tk.Toplevel(self.parent)
        win.title("MCAddon Translator PRO")
        win.geometry("760x560")
        win.configure(bg=DARK)
        win.resizable(False, False)

        tk.Label(
            win,
            text="MCAddon Translator PRO",
            bg=DARK,
            fg=GOLD,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=22, pady=(22, 6))

        tk.Label(
            win,
            text=f"「{feature_name}」はPro版で利用できます",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 16))

        card = tk.Frame(
            win,
            bg=GLASS,
            highlightthickness=1,
            highlightbackground=ACCENT,
            bd=0
        )
        card.pack(fill="both", expand=True, padx=22, pady=10)

        features = [
            ("翻訳履歴", "過去の翻訳を一覧で確認できます"),
            ("比較プレビュー", "原文と翻訳結果を並べて確認できます"),
            ("再翻訳", "気になる翻訳だけを再生成できます"),
            ("ユーザー辞書編集", "固有名詞やアイテム名を自由に登録できます"),
            ("詳細設定", "GPT / Ollama などの翻訳エンジン設定を管理できます"),
            ("統計画面", "AI使用回数やキャッシュ効果を確認できます"),
            ("今後追加予定", "AIレビュー・共有辞書・翻訳品質強化")
        ]

        for title, desc in features:
            row = tk.Frame(card, bg=GLASS)
            row.pack(fill="x", padx=18, pady=6)

            tk.Label(
                row,
                text="✓",
                bg=GLASS,
                fg=ACCENT,
                font=("Segoe UI", 13, "bold"),
                width=3
            ).pack(side="left")

            text_area = tk.Frame(row, bg=GLASS)
            text_area.pack(side="left", fill="x", expand=True)

            tk.Label(
                text_area,
                text=title,
                bg=GLASS,
                fg=TEXT,
                font=("Segoe UI", 11, "bold")
            ).pack(anchor="w")

            tk.Label(
                text_area,
                text=desc,
                bg=GLASS,
                fg=SUB,
                font=("Segoe UI", 9)
            ).pack(anchor="w")

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=22, pady=(8, 18))

        ttk.Button(
            btns,
            text="あとで",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=5)

        ttk.Button(
            btns,
            text="Pro版について",
            command=self.show_purchase_info,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="right", padx=5)

        self._log(f"🔒 PRO誘導表示: {feature_name}")

    def show_purchase_info(self):
        messagebox.showinfo(
            "Pro版について",
            "Pro版では、履歴・辞書編集・再翻訳・詳細設定・統計などが利用できます。\n\n"
            "今後、購入ページやBOOTH/Stripeリンクをここに接続します。"
        )

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)