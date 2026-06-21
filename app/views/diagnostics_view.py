import tkinter as tk
from tkinter import ttk, messagebox

from core.addon_diagnostics import AddonDiagnostics


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
ACCENT = "#00e5ff"


class DiagnosticsView:
    def __init__(self, parent, processor=None, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.diagnostics = AddonDiagnostics()

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("アドオン診断 - PRO")
        win.geometry("940x620")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="ADDON DIAGNOSTICS",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        summary = tk.Label(
            win,
            text="アドオン構成・翻訳状態を診断します",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        )
        summary.pack(anchor="w", padx=16, pady=(0, 8))

        table_frame = tk.Frame(win, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT)
        table_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("status", "item", "detail")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("status", text="状態")
        self.tree.heading("item", text="項目")
        self.tree.heading("detail", text="詳細")
        self.tree.column("status", width=90, stretch=False)
        self.tree.column("item", width=180, stretch=False)
        self.tree.column("detail", width=650, stretch=True)

        ybar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<MouseWheel>", lambda e: self.tree.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=12)

        ttk.Button(
            btns,
            text="診断開始",
            command=lambda: self.run_diagnostics(summary),
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="選択行をコピー",
            command=self.copy_selected,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

    def run_diagnostics(self, summary_label):
        for item in self.tree.get_children():
            self.tree.delete(item)

        root_path = None
        if self.processor:
            root_path = getattr(self.processor, "scan_root", None) or getattr(self.processor, "source_path", None)

        if not root_path:
            messagebox.showinfo("確認", "先に翻訳、またはアドオン選択を実行してください。")
            return

        report = self.diagnostics.run(root_path)
        counts = {"OK": 0, "WARN": 0, "ERROR": 0, "INFO": 0}

        for row in report:
            status = row.get("status", "INFO")
            counts[status] = counts.get(status, 0) + 1
            self.tree.insert("", "end", values=(status, row.get("item", ""), row.get("detail", "")))

        summary_label.config(text=f"診断結果: OK {counts.get('OK', 0)} / WARN {counts.get('WARN', 0)} / ERROR {counts.get('ERROR', 0)}")

        if self.on_log:
            self.on_log(f"🧪 アドオン診断: OK {counts.get('OK', 0)} / WARN {counts.get('WARN', 0)} / ERROR {counts.get('ERROR', 0)}")

    def copy_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("コピー", "コピーする行を選択してください。")
            return
        values = self.tree.item(selected[0], "values")
        text = " | ".join(str(v) for v in values)
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        messagebox.showinfo("コピー", "選択行をコピーしました。")
