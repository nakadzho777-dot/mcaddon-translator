import os
import tkinter as tk
from tkinter import ttk, messagebox

from core.quality_score import QualityScoreAnalyzer


DARK = "#020617"
GLASS = "#07111f"
TEXT = "#f8fafc"
SUB = "#cbd5e1"
ACCENT = "#00e5ff"


class QualityScoreView:
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
        self.analyzer = QualityScoreAnalyzer()

        self.score_label = None
        self.summary_label = None
        self.tree = None

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("翻訳品質スコア - PRO")
        win.geometry("960x640")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="QUALITY SCORE",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 4))

        tk.Label(
            win,
            text="翻訳結果の日本語率・未翻訳・JSON異常・要確認項目から品質を評価します。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 10))

        top = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        top.pack(fill="x", padx=16, pady=(0, 10))

        self.score_label = tk.Label(
            top,
            text="品質スコア: -",
            bg=GLASS,
            fg=ACCENT,
            font=("Segoe UI", 24, "bold")
        )
        self.score_label.pack(anchor="w", padx=14, pady=(10, 2))

        self.summary_label = tk.Label(
            top,
            text="まだ分析していません",
            bg=GLASS,
            fg=TEXT,
            font=("Segoe UI", 10),
            justify="left"
        )
        self.summary_label.pack(anchor="w", padx=14, pady=(0, 12))

        table_frame = tk.Frame(win, bg=DARK)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("type", "file", "line", "message")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("type", text="種類")
        self.tree.heading("file", text="ファイル")
        self.tree.heading("line", text="行")
        self.tree.heading("message", text="内容")

        self.tree.column("type", width=130)
        self.tree.column("file", width=330)
        self.tree.column("line", width=70, anchor="center")
        self.tree.column("message", width=420)

        ybar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=12)

        ttk.Button(
            btns,
            text="品質スコアを分析",
            command=self.analyze,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        self.analyze()

    def _target_path(self):
        if not self.processor:
            return None

        return (
            getattr(self.processor, "output_path", None)
            or getattr(self.processor, "source_path", None)
            or getattr(self.processor, "scan_root", None)
        )

    def _clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def analyze(self):
        path = self._target_path()

        if not path:
            messagebox.showinfo("品質スコア", "先に翻訳を実行してください。")
            return

        result = self.analyzer.analyze(path)

        score = result.get("score", 0)
        total = result.get("total_texts", 0)
        jp = result.get("japanese_texts", 0)
        untranslated = len(result.get("untranslated", []))
        mixed = len(result.get("mixed", []))
        json_errors = len(result.get("json_errors", []))
        risks = len(result.get("risk_items", []))

        self.score_label.config(text=f"品質スコア: {score} 点")

        jp_rate = 0
        if total:
            jp_rate = round((jp / total) * 100, 1)

        self.summary_label.config(
            text=(
                f"日本語率: {jp_rate}% / 対象テキスト: {total}件 / "
                f"未翻訳候補: {untranslated}件 / 英語混在: {mixed}件 / "
                f"JSON異常: {json_errors}件 / 要確認: {risks}件"
            )
        )

        self._clear_tree()

        for item in result.get("untranslated", []):
            self.tree.insert(
                "",
                "end",
                values=(
                    "未翻訳候補",
                    item.get("file", ""),
                    item.get("line", ""),
                    item.get("text", "")
                )
            )

        for item in result.get("mixed", []):
            self.tree.insert(
                "",
                "end",
                values=(
                    "英語混在",
                    item.get("file", ""),
                    item.get("line", ""),
                    item.get("text", "")
                )
            )

        for item in result.get("json_errors", []):
            self.tree.insert(
                "",
                "end",
                values=(
                    "JSON異常",
                    item.get("file", ""),
                    "-",
                    item.get("error", "")
                )
            )

        for item in result.get("risk_items", []):
            self.tree.insert(
                "",
                "end",
                values=(
                    "要確認",
                    item.get("file", ""),
                    "-",
                    item.get("issue", "")
                )
            )

        if self.on_log:
            self.on_log(f"🏆 品質スコア: {score}点")
