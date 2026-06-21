import tkinter as tk
from tkinter import ttk, messagebox

from core.quality_analyzer import QualityAnalyzer


DARK = "#020617"
TEXT = "#f8fafc"
SUB = "#cbd5e1"


class QualityView:

    def __init__(
        self,
        parent,
        processor=None,
        on_log=None,
        style_prefix="Launcher"
    ):
        self.parent = parent
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix

        self.analyzer = QualityAnalyzer()

    def open(self):

        win = tk.Toplevel(self.parent)

        win.title("翻訳品質チェッカー")
        win.geometry("900x560")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="QUALITY CHECK",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        self.tree = ttk.Treeview(
            win,
            columns=("file", "issue"),
            show="headings"
        )

        self.tree.heading("file", text="ファイル")
        self.tree.heading("issue", text="問題")

        self.tree.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=10
        )

        ttk.Button(
            win,
            text="スキャン",
            command=self.scan
        ).pack(pady=8)

    def scan(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        path = (
            getattr(self.processor, "output_path", None)
            or getattr(self.processor, "source_path", None)
        )

        if not path:

            messagebox.showinfo(
                "確認",
                "先に翻訳を実行してください"
            )
            return

        results = self.analyzer.scan(path)

        for item in results:

            self.tree.insert(
                "",
                "end",
                values=(
                    item["file"],
                    item["issue"]
                )
            )

        if self.on_log:
            self.on_log(
                f"🔍 品質チェック: {len(results)}件"
            )