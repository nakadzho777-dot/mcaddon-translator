import tkinter as tk
from tkinter import ttk, messagebox


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
BUTTON_DARK = "#0f2138"
ACCENT = "#00e5ff"


class PreviewView:
    def __init__(self, parent, translator, on_log=None, on_stats_update=None, style_prefix="Launcher"):
        self.parent = parent
        self.translator = translator
        self.on_log = on_log
        self.on_stats_update = on_stats_update
        self.style_prefix = style_prefix

    def open(self, item=None):
        win = tk.Toplevel(self.parent)
        win.title("翻訳プレビュー")
        win.geometry("940x560")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="TRANSLATION PREVIEW",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        body = tk.Frame(win, bg=DARK)
        body.pack(fill="both", expand=True, padx=16, pady=8)

        left = tk.Frame(body, bg=DARK)
        right = tk.Frame(body, bg=DARK)

        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            left,
            text="原文",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        source_box = tk.Text(
            left,
            bg=GLASS,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            wrap="word"
        )
        source_box.pack(fill="both", expand=True)

        tk.Label(
            right,
            text="翻訳結果",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        result_box = tk.Text(
            right,
            bg=GLASS,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            wrap="word"
        )
        result_box.pack(fill="both", expand=True)

        if item:
            source_box.insert("end", item.get("source", ""))
            result_box.insert("end", item.get("result", ""))

        btn = tk.Frame(win, bg=DARK)
        btn.pack(fill="x", padx=16, pady=12)

        def retranslate():
            source = source_box.get("1.0", "end").strip()
            if not source:
                messagebox.showinfo("Info", "原文が空です")
                return

            result = self.translator.retranslate(source)
            result_box.delete("1.0", "end")
            result_box.insert("end", result)

            self._stats()
            self._log("🔁 プレビュー再翻訳")

        def add_dict():
            source = source_box.get("1.0", "end").strip()
            result = result_box.get("1.0", "end").strip()

            if not source or not result:
                messagebox.showinfo("Info", "原文と翻訳結果を入力してください")
                return

            self.translator.add_user_word(source, result)
            self._stats()
            self._log("📘 プレビューから辞書登録")
            messagebox.showinfo("辞書登録", "ユーザー辞書に登録しました")

        ttk.Button(
            btn,
            text="再翻訳",
            command=retranslate,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btn,
            text="辞書登録",
            command=add_dict,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btn,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)

    def _stats(self):
        if self.on_stats_update:
            self.on_stats_update()