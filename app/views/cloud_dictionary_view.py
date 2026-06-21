import tkinter as tk
from tkinter import ttk, messagebox

from core.cloud_dictionary import CloudDictionary


DARK = "#020617"
GLASS = "#07111f"
TEXT = "#f8fafc"
SUB = "#cbd5e1"
ACCENT = "#00e5ff"


class CloudDictionaryView:
    def __init__(self, parent, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.cloud = CloudDictionary()

        self.total_label = None
        self.url_label = None
        self.tree = None

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("クラウド辞書 - PRO")
        win.geometry("940x620")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="CLOUD DICTIONARY",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 4))

        tk.Label(
            win,
            text="Railway上の共有辞書を確認・同期します。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 10))

        info = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        info.pack(fill="x", padx=16, pady=(0, 10))

        self.total_label = tk.Label(
            info,
            text="総登録数: -",
            bg=GLASS,
            fg=TEXT,
            font=("Segoe UI", 12, "bold")
        )
        self.total_label.pack(anchor="w", padx=12, pady=(10, 2))

        self.url_label = tk.Label(
            info,
            text="URL: 読み込み中...",
            bg=GLASS,
            fg=SUB,
            font=("Segoe UI", 9),
            wraplength=850,
            justify="left"
        )
        self.url_label.pack(anchor="w", padx=12, pady=(0, 10))

        table_frame = tk.Frame(win, bg=DARK)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("source", "translated", "count")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("source", text="原文 / 登録語")
        self.tree.heading("translated", text="翻訳")
        self.tree.heading("count", text="使用回数")

        self.tree.column("source", width=360)
        self.tree.column("translated", width=360)
        self.tree.column("count", width=100, anchor="center")

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
            text="サーバー統計を更新",
            command=self.refresh,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="サーバー辞書をローカルへ同期",
            command=self.sync_from_server,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="ローカル辞書を表示",
            command=self.show_local,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        self.refresh()

    def _clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def refresh(self):
        self.cloud.reload()

        if self.url_label:
            self.url_label.config(
                text=f"URL: {self.cloud.server_url or '未設定'}"
            )

        stats = self.cloud.stats()

        total = stats.get("total", 0)
        self.total_label.config(text=f"総登録数: {total}")

        self._clear_tree()

        top = stats.get("top", [])

        if not top:
            self.tree.insert(
                "",
                "end",
                values=("まだ人気翻訳データがありません", "", "")
            )
        else:
            for item in top:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        item.get("source", ""),
                        item.get("translated", ""),
                        item.get("count", "")
                    )
                )

        if self.on_log:
            self.on_log(f"☁ クラウド辞書統計: {total}件")

    def sync_from_server(self):
        ok = self.cloud.sync_from_server()

        if ok:
            messagebox.showinfo(
                "クラウド辞書",
                "サーバー辞書をローカルへ同期しました。"
            )
            if self.on_log:
                self.on_log("☁ クラウド辞書をローカルへ同期")
            self.show_local()
        else:
            messagebox.showerror(
                "クラウド辞書",
                "同期に失敗しました。"
            )

    def show_local(self):
        data = self.cloud.load()

        self._clear_tree()

        self.total_label.config(
            text=f"ローカル登録数: {len(data)}"
        )

        if not data:
            self.tree.insert(
                "",
                "end",
                values=("ローカル辞書は空です", "", "")
            )
            return

        for source, translated in data.items():
            self.tree.insert(
                "",
                "end",
                values=(source, translated, "")
            )
