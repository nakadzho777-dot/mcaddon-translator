import tkinter as tk
from tkinter import ttk, messagebox

from core.translation_checker import TranslationChecker


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#00e5ff"


class CheckerView:
    def __init__(self, parent, processor=None, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.checker = TranslationChecker()

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("翻訳漏れ検出 - PRO")
        win.geometry("920x620")
        win.minsize(760, 480)
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="TRANSLATION CHECKER",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold"),
        ).pack(anchor="w", padx=16, pady=(14, 8))

        top = tk.Frame(win, bg=DARK)
        top.pack(fill="x", padx=16, pady=(0, 8))

        self.summary = tk.Label(
            top,
            text="翻訳後のファイルから、英語が残っていそうな箇所を検出します。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold"),
        )
        self.summary.pack(side="left")

        table_frame = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("type", "line", "key", "text", "file")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {
            "type": "種類",
            "line": "行",
            "key": "キー",
            "text": "未翻訳らしき文字",
            "file": "ファイル",
        }
        widths = {"type": 70, "line": 60, "key": 220, "text": 300, "file": 360}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

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
            text="検出開始",
            command=self.run_check,
            style=f"{self.style_prefix}.Accent.TButton",
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="選択テキストをコピー",
            command=self.copy_selected,
            style=f"{self.style_prefix}.Dark.TButton",
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton",
        ).pack(side="right", padx=4)

    def run_check(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        root_path = None
        if self.processor:
            root_path = getattr(self.processor, "scan_root", None) or getattr(self.processor, "source_path", None)

        if not root_path:
            messagebox.showinfo("確認", "先に翻訳を実行してください。")
            return

        issues = self.checker.check(root_path)
        for issue in issues:
            self.tree.insert(
                "",
                "end",
                values=(
                    issue.get("type", ""),
                    issue.get("line", ""),
                    issue.get("key", ""),
                    issue.get("text", ""),
                    issue.get("file", ""),
                ),
            )

        self.summary.config(text=f"検出結果: {len(issues)} 件")
        if self.on_log:
            self.on_log(f"🔍 翻訳漏れ検出: {len(issues)} 件")

    def copy_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("コピー", "コピーする行を選択してください。")
            return

        values = self.tree.item(selected[0], "values")
        text = values[3] if len(values) >= 4 else ""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        messagebox.showinfo("コピー", "未翻訳テキストをコピーしました。")
