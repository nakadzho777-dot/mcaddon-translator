import tkinter as tk
from tkinter import ttk


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#00e5ff"


class StatsView:
    def __init__(
        self,
        parent,
        translator,
        on_log=None,
        style_prefix="Launcher"
    ):
        self.parent = parent
        self.translator = translator
        self.on_log = on_log
        self.style_prefix = style_prefix

    def open(self):
        stats = self._safe_stats()

        ai = int(stats.get("ai", 0))
        cache = int(stats.get("cache", 0))
        dictionary = int(stats.get("dictionary", 0))

        total = ai + cache + dictionary
        cache_rate = 0
        if total:
            cache_rate = round((cache / total) * 100, 1)

        win = tk.Toplevel(self.parent)
        win.title("統計")
        win.geometry("780x500")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="TRANSLATION STATS",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        main = self._card(win)
        main.pack(fill="both", expand=True, padx=16, pady=10)

        grid = tk.Frame(main, bg=GLASS)
        grid.pack(fill="x", padx=16, pady=18)

        self._stat_card(grid, "AI翻訳", ai, 0, 0)
        self._stat_card(grid, "キャッシュ", cache, 0, 1)
        self._stat_card(grid, "辞書", dictionary, 0, 2)
        self._stat_card(grid, "合計", total, 1, 0)
        self._stat_card(grid, "キャッシュ率", f"{cache_rate}%", 1, 1)
        self._stat_card(grid, "節約目安", f"{cache + dictionary} 回", 1, 2)

        desc = tk.Text(
            main,
            height=6,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            wrap="word"
        )
        desc.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        desc.insert("end", "統計の見方\n\n")
        desc.insert("end", "AI翻訳: 実際にAIへ送信した翻訳回数です。\n")
        desc.insert("end", "キャッシュ: 過去の翻訳結果を再利用した回数です。\n")
        desc.insert("end", "辞書: ユーザー辞書やMinecraft辞書で処理した回数です。\n")
        desc.insert("end", "キャッシュ率が高いほど、速度とコスト効率が良い状態です。\n")
        desc.config(state="disabled")

        btns = tk.Frame(main, bg=GLASS)
        btns.pack(fill="x", padx=16, pady=(0, 14))

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        self._log("📊 統計画面を開きました")

    def _stat_card(self, parent, title, value, row, col):
        card = tk.Frame(
            parent,
            bg=GLASS_DARK,
            highlightthickness=1,
            highlightbackground=ACCENT,
            bd=0
        )
        card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

        parent.grid_columnconfigure(col, weight=1)

        tk.Label(
            card,
            text=title,
            bg=GLASS_DARK,
            fg=SUB,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))

        tk.Label(
            card,
            text=str(value),
            bg=GLASS_DARK,
            fg=ACCENT,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def _safe_stats(self):
        try:
            stats = self.translator.stats()
            if isinstance(stats, dict):
                return stats
        except Exception:
            pass

        return {
            "ai": 0,
            "cache": 0,
            "dictionary": 0
        }

    def _card(self, parent):
        return tk.Frame(
            parent,
            bg=GLASS,
            highlightthickness=1,
            highlightbackground=ACCENT,
            bd=0
        )

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)