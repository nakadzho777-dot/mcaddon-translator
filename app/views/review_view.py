import threading
import tkinter as tk
from tkinter import ttk, messagebox

from core.ai_reviewer import AIReviewer


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
ACCENT = "#00e5ff"


class ReviewView:
    def __init__(self, parent, translator, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.translator = translator
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.reviewer = AIReviewer()
        self.tree = None
        self.summary = None

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("AIレビュー - PRO")
        win.geometry("980x640")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="AI REVIEW",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        self.summary = tk.Label(
            win,
            text="翻訳履歴をAIレビューします",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        )
        self.summary.pack(anchor="w", padx=16, pady=(0, 8))

        frame = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("score", "source", "result", "suggestion", "reason", "engine")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")

        headers = {
            "score": "点数",
            "source": "原文",
            "result": "翻訳",
            "suggestion": "改善案",
            "reason": "理由",
            "engine": "方式",
        }
        widths = {
            "score": 60,
            "source": 220,
            "result": 220,
            "suggestion": 220,
            "reason": 360,
            "engine": 80,
        }
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], minwidth=60, stretch=True)

        ybar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=12)

        ttk.Button(
            btns,
            text="レビュー開始",
            command=self.run_review,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="改善案をコピー",
            command=self.copy_suggestion,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

    def run_review(self):
        if not self.tree:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        history = []
        try:
            history = self.translator.get_history()
        except Exception:
            history = []

        if not history:
            messagebox.showinfo("AIレビュー", "翻訳履歴がありません。先に翻訳してください。")
            return

        self.summary.config(text="レビュー中...")
        if self.on_log:
            self.on_log("🧠 AIレビュー開始")

        def job():
            reviews = self.reviewer.review_history(history)
            self.parent.after(0, lambda: self._show_reviews(reviews))

        threading.Thread(target=job, daemon=True).start()

    def _show_reviews(self, reviews):
        for r in reviews:
            self.tree.insert(
                "",
                "end",
                values=(
                    r.get("score", ""),
                    r.get("source", ""),
                    r.get("result", ""),
                    r.get("suggestion", ""),
                    r.get("reason", ""),
                    r.get("engine", ""),
                )
            )

        self.summary.config(text=f"レビュー結果: {len(reviews)} 件")
        if self.on_log:
            self.on_log(f"🧠 AIレビュー完了: {len(reviews)} 件")

    def copy_suggestion(self):
        selected = self.tree.selection() if self.tree else []
        if not selected:
            messagebox.showinfo("コピー", "コピーする行を選択してください。")
            return
        values = self.tree.item(selected[0], "values")
        text = values[3] if len(values) >= 4 else ""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        messagebox.showinfo("コピー", "改善案をコピーしました。")
