import tkinter as tk
from tkinter import ttk, messagebox

from core.json_repair import JsonRepair


DARK = "#020617"
TEXT = "#f8fafc"
SUB = "#cbd5e1"


class JsonRepairView:
    def __init__(self, parent, processor=None, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.repairer = JsonRepair()

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("JSON修復 - PRO")
        win.geometry("900x560")
        win.configure(bg=DARK)

        tk.Label(win, text="JSON REPAIR", bg=DARK, fg=TEXT, font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=16, pady=(14, 8))
        tk.Label(win, text="JSON構文エラーを検出し、簡易修復します。", bg=DARK, fg=SUB, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(0, 10))

        frame = tk.Frame(win, bg=DARK)
        frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("file", "error")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("file", text="ファイル")
        self.tree.heading("error", text="エラー内容")
        self.tree.column("file", width=360)
        self.tree.column("error", width=480)

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

        ttk.Button(btns, text="スキャン", command=self.scan, style=f"{self.style_prefix}.Accent.TButton").pack(side="left", padx=4)
        ttk.Button(btns, text="選択ファイルを修復", command=self.repair_selected, style=f"{self.style_prefix}.Dark.TButton").pack(side="left", padx=4)
        ttk.Button(btns, text="閉じる", command=win.destroy, style=f"{self.style_prefix}.Dark.TButton").pack(side="right", padx=4)

    def _target_path(self):
        if not self.processor:
            return None
        return (
            getattr(self.processor, "output_path", None)
            or getattr(self.processor, "source_path", None)
            or getattr(self.processor, "scan_root", None)
        )

    def scan(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        path = self._target_path()
        if not path:
            messagebox.showinfo("確認", "先に翻訳を実行してください。")
            return

        results = self.repairer.scan(path)
        for item in results:
            self.tree.insert("", "end", values=(item.get("file", ""), item.get("error", "")))

        if self.on_log:
            self.on_log(f"🧩 JSON修復スキャン: {len(results)}件")

        if not results:
            messagebox.showinfo("JSON修復", "JSONエラーは見つかりませんでした。")

    def repair_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("JSON修復", "修復するファイルを選択してください。")
            return

        values = self.tree.item(selected[0], "values")
        path = values[0]
        ok = self.repairer.repair(path)

        if ok:
            messagebox.showinfo("JSON修復", "修復を実行しました。再スキャンしてください。")
            if self.on_log:
                self.on_log(f"🛠 JSON修復: {path}")
        else:
            messagebox.showerror("JSON修復", "修復に失敗しました。")
