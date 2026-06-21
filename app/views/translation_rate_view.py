import tkinter as tk
from tkinter import ttk, messagebox

from core.translation_stats import TranslationStats


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
ACCENT = "#00e5ff"


class TranslationRateView:
    def __init__(self, parent, processor=None, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.stats = TranslationStats()

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("翻訳率表示")
        win.geometry("720x460")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="TRANSLATION RATE",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        self.summary = tk.Label(
            win,
            text="翻訳率を計算します。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        )
        self.summary.pack(anchor="w", padx=16, pady=(0, 10))

        card = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        card.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("name", "value")
        self.tree = ttk.Treeview(card, columns=columns, show="headings")
        self.tree.heading("name", text="項目")
        self.tree.heading("value", text="値")
        self.tree.column("name", width=240)
        self.tree.column("value", width=320)

        ybar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ybar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        ybar.pack(side="right", fill="y")

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=12)

        ttk.Button(
            btns,
            text="再計算",
            command=self.refresh,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        self.refresh()

    def _target_path(self):
        if not self.processor:
            return None
        return (
            getattr(self.processor, "scan_root", None)
            or getattr(self.processor, "source_path", None)
            or getattr(self.processor, "output_path", None)
        )

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        path = self._target_path()
        if not path:
            messagebox.showinfo("翻訳率", "先に翻訳を実行してください。")
            return

        result = self.stats.analyze(path)

        rows = [
            ("翻訳率", f"{result['rate']}%"),
            ("翻訳対象数", str(result["total"])),
            ("翻訳済み", str(result["translated"])),
            ("未翻訳らしき項目", str(result["untranslated"])),
            ("対象ファイル数", str(result["files"])),
            ("対象パス", path),
        ]

        for row in rows:
            self.tree.insert("", "end", values=row)

        self.summary.config(
            text=f"翻訳率: {result['rate']}% / 未翻訳らしき項目: {result['untranslated']}件"
        )

        if self.on_log:
            self.on_log(f"📊 翻訳率: {result['rate']}% / 未翻訳: {result['untranslated']}件")
