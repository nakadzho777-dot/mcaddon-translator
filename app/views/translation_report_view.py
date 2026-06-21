import os
import tkinter as tk
from tkinter import ttk, messagebox

from core.translation_report import TranslationReportGenerator


DARK = "#020617"
GLASS = "#07111f"
TEXT = "#f8fafc"
SUB = "#cbd5e1"
ACCENT = "#00e5ff"


class TranslationReportView:
    def __init__(
        self,
        parent,
        translator=None,
        processor=None,
        on_log=None,
        style_prefix="Launcher"
    ):
        self.parent = parent
        self.translator = translator
        self.processor = processor
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.generator = TranslationReportGenerator(translator, processor)

        self.last_json = None
        self.last_txt = None
        self.text_box = None

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("翻訳レポート - PRO")
        win.geometry("900x620")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="TRANSLATION REPORT",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 4))

        tk.Label(
            win,
            text="翻訳結果の統計レポートを生成します。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=16, pady=(0, 10))

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

        ybar = ttk.Scrollbar(frame, orient="vertical", command=self.text_box.yview)
        self.text_box.configure(yscrollcommand=ybar.set)

        self.text_box.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        ybar.pack(side="right", fill="y")

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=12)

        ttk.Button(
            btns,
            text="レポート生成",
            command=self.generate_report,
            style=f"{self.style_prefix}.Accent.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="TXTを開く",
            command=self.open_txt,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="reportsフォルダを開く",
            command=self.open_reports_folder,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        self.generate_report()

    def generate_report(self):
        try:
            result = self.generator.generate()

            self.last_json = result.get("json")
            self.last_txt = result.get("txt")

            report = result.get("report", {})
            stats = report.get("stats", {})

            elapsed = report.get("elapsed_seconds")
            elapsed_text = "-" if elapsed is None else f"{elapsed:.2f} 秒"

            lines = []
            lines.append("MCAddon Translator 翻訳レポート")
            lines.append("=" * 40)
            lines.append(f"作成日時: {report.get('created_at')}")
            lines.append(f"入力: {report.get('source_path')}")
            lines.append(f"出力: {report.get('output_path')}")
            lines.append(f"処理時間: {elapsed_text}")
            lines.append("")
            lines.append("[翻訳統計]")
            lines.append(f"総処理数: {stats.get('total', 0)}")
            lines.append(f"AI翻訳: {stats.get('ai', 0)}")
            lines.append(f"キャッシュ: {stats.get('cache', 0)}")
            lines.append(f"辞書ヒット: {stats.get('dictionary', 0)}")
            lines.append(f"クラウド辞書: {stats.get('cloud', 0)}")
            lines.append(f"再翻訳: {stats.get('retranslate', 0)}")
            lines.append(f"エラー: {stats.get('error', 0)}")
            lines.append("")
            lines.append(f"JSON: {self.last_json}")
            lines.append(f"TXT: {self.last_txt}")

            self.text_box.delete("1.0", "end")
            self.text_box.insert("end", "\n".join(lines))

            if self.on_log:
                self.on_log(f"📄 翻訳レポート生成: {self.last_txt}")

        except Exception as e:
            messagebox.showerror("翻訳レポート", f"生成に失敗しました。\n{e}")

    def open_txt(self):
        if not self.last_txt or not os.path.exists(self.last_txt):
            messagebox.showinfo("翻訳レポート", "先にレポートを生成してください。")
            return

        try:
            os.startfile(self.last_txt)
        except Exception as e:
            messagebox.showerror("翻訳レポート", f"TXTを開けませんでした。\n{e}")

    def open_reports_folder(self):
        os.makedirs("reports", exist_ok=True)

        try:
            os.startfile("reports")
        except Exception as e:
            messagebox.showerror("翻訳レポート", f"reportsフォルダを開けませんでした。\n{e}")
