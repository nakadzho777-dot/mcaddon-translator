import tkinter as tk
from tkinter import ttk, messagebox

from core.update_checker import UpdateChecker


DARK = "#020617"
GLASS = "#07111f"
TEXT = "#f8fafc"
SUB = "#cbd5e1"
ACCENT = "#00e5ff"


class UpdateView:
    def __init__(self, parent, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.checker = UpdateChecker()

        self.info_label = None
        self.text_box = None
        self.download_url = ""

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("アップデート確認")
        win.geometry("760x520")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="UPDATE CHECKER",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 4))

        self.info_label = tk.Label(
            win,
            text="更新情報を確認します。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10),
            justify="left"
        )
        self.info_label.pack(anchor="w", padx=16, pady=(0, 10))

        frame = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.text_box = tk.Text(
            frame,
            bg=GLASS,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            wrap="word",
            font=("Consolas", 10)
        )
        self.text_box.pack(fill="both", expand=True, padx=10, pady=10)

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=12)

        ttk.Button(
            btns,
            text="更新確認",
            command=self.check_update,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="ダウンロードページを開く",
            command=self.open_download,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        self.check_update()

    def check_update(self):
        result = self.checker.check()

        current = result.get("current", "-")
        latest = result.get("latest", "-")
        self.download_url = result.get("download_url", "")

        self.text_box.delete("1.0", "end")

        if not result.get("ok"):
            self.info_label.config(text="更新確認に失敗しました。")
            self.text_box.insert("end", result.get("message", "不明なエラー"))
            if self.on_log:
                self.on_log("⚠ 更新確認に失敗")
            return

        if result.get("update_available"):
            self.info_label.config(
                text=f"新しいバージョンがあります。現在: {current} / 最新: {latest}"
            )
            self.text_box.insert("end", f"現在のバージョン: {current}\n")
            self.text_box.insert("end", f"最新バージョン: {latest}\n\n")
            self.text_box.insert("end", "更新内容:\n")

            for note in result.get("notes", []):
                self.text_box.insert("end", f"・{note}\n")

            if self.download_url:
                self.text_box.insert("end", f"\nダウンロードURL:\n{self.download_url}\n")

            if self.on_log:
                self.on_log(f"⬆ 更新あり: {current} → {latest}")
        else:
            self.info_label.config(
                text=f"最新版です。現在: {current}"
            )
            self.text_box.insert("end", f"現在のバージョン: {current}\n")
            self.text_box.insert("end", "最新版です。\n")

            if self.on_log:
                self.on_log("✅ 最新版を使用中")

    def open_download(self):
        if not self.download_url:
            messagebox.showinfo("アップデート", "ダウンロードURLがありません。")
            return

        self.checker.open_download(self.download_url)
