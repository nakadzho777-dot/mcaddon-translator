import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from core.translator import Translator
from core.processor import MCAddonProcessor
from core.updater import Updater
from core.license import LicenseManager
from core.utils import base_path


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("MCAddon Translator PRO")
        self.root.geometry("760x430")

        self.translator = Translator()
        self.processor = MCAddonProcessor()
        self.updater = Updater(version="1.0.0")
        self.license = LicenseManager()

        self.is_pro = False
        self.license_key = ""

        if not self._license_gate():
            self.root.destroy()
            return

        self._build_ui()
        self._check_update_startup()

    def _license_gate(self):
        cache = self.license.load_cache()

        if cache:
            cached_key = cache.get("license_key", "")
            if cached_key and self.license.verify(cached_key):
                self.is_pro = True
                self.license_key = cached_key
                return True

        win = tk.Toplevel(self.root)
        win.title("ライセンス認証")
        win.geometry("430x220")
        win.resizable(False, False)

        ttk.Label(win, text="MCAddon Translator Pro ライセンス認証", font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(win, text="ライセンスキーを入力してください").pack(pady=5)

        entry = ttk.Entry(win, width=48)
        entry.pack(pady=5)

        if cache:
            entry.insert(0, cache.get("license_key", ""))

        result = {"ok": False}

        def verify():
            key = entry.get().strip()

            if not key:
                messagebox.showerror("ライセンス", "ライセンスキーを入力してください")
                return

            if self.license.verify(key):
                self.is_pro = True
                self.license_key = key
                result["ok"] = True
                messagebox.showinfo("ライセンス", "Proライセンス認証に成功しました")
                win.destroy()
            else:
                messagebox.showerror("ライセンス", "ライセンス認証に失敗しました")

        def cancel():
            result["ok"] = False
            win.destroy()

        btn = ttk.Frame(win)
        btn.pack(pady=15)

        ttk.Button(btn, text="認証", command=verify).grid(row=0, column=0, padx=5)
        ttk.Button(btn, text="終了", command=cancel).grid(row=0, column=1, padx=5)

        ttk.Label(win, text="※一度認証すると次回から自動認証されます", foreground="gray").pack()

        win.transient(self.root)
        win.grab_set()
        self.root.wait_window(win)

        return result["ok"]

    def _build_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=12, pady=12, fill="both", expand=True)

        header = ttk.Frame(frame)
        header.pack(fill="x", pady=5)

        ttk.Label(header, text="MCAddon Translator", font=("Arial", 16, "bold")).pack(side="left")

        self.plan_label = ttk.Label(
            header,
            text="PRO 認証済み" if self.is_pro else "FREE",
            foreground="green" if self.is_pro else "gray"
        )
        self.plan_label.pack(side="right")

        self.progress = ttk.Progressbar(frame, length=700)
        self.progress.pack(pady=10)

        self.status = ttk.Label(frame, text="待機中")
        self.status.pack()

        btn = ttk.Frame(frame)
        btn.pack(pady=12)

        ttk.Button(btn, text="翻訳開始", command=self.run).grid(row=0, column=0, padx=5)
        ttk.Button(btn, text="翻訳履歴", command=self.translation_history).grid(row=0, column=1, padx=5)
        ttk.Button(btn, text="設定", command=self.settings).grid(row=0, column=2, padx=5)
        ttk.Button(btn, text="ログ", command=self.logs).grid(row=0, column=3, padx=5)
        ttk.Button(btn, text="更新確認", command=self.manual_update).grid(row=0, column=4, padx=5)
        ttk.Button(btn, text="ライセンス", command=self.license_settings).grid(row=0, column=5, padx=5)

        info = ttk.LabelFrame(frame, text="Pro機能")
        info.pack(fill="x", pady=10)

        ttk.Label(
            info,
            text="翻訳履歴・再翻訳・一括翻訳・AI翻訳補助が利用できます。"
        ).pack(anchor="w", padx=10, pady=8)

    def license_settings(self):
        win = tk.Toplevel(self.root)
        win.title("ライセンス設定")
        win.geometry("460x210")
        win.resizable(False, False)

        ttk.Label(win, text="ライセンスキー", font=("Arial", 11, "bold")).pack(pady=10)

        var = tk.StringVar(value=self.license_key)
        ttk.Entry(win, textvariable=var, width=52).pack(pady=5)

        def verify_and_save():
            key = var.get().strip()

            if not key:
                messagebox.showerror("ライセンス", "キーを入力してください")
                return

            if self.license.verify(key):
                self.is_pro = True
                self.license_key = key
                self.plan_label.config(text="PRO 認証済み", foreground="green")
                messagebox.showinfo("ライセンス", "認証に成功しました")
                win.destroy()
            else:
                messagebox.showerror("ライセンス", "認証に失敗しました")

        ttk.Button(win, text="認証して保存", command=verify_and_save).pack(pady=10)
        ttk.Label(win, text="購入後に発行された MCA-PRO-... のキーを入力してください。", foreground="gray").pack()

    def run(self):
        if not self.is_pro:
            messagebox.showerror("ライセンス", "Proライセンス認証が必要です")
            return

        path = filedialog.askdirectory()
        if not path:
            return

        threading.Thread(target=self._job, args=(path,), daemon=True).start()

    def _job(self, path):
        self.root.after(0, lambda: self.status.config(text="スキャン中..."))

        files = self.processor.scan(path)

        if not files:
            self.root.after(0, lambda: messagebox.showinfo("Info", "対象なし"))
            self.root.after(0, lambda: self.status.config(text="対象なし"))
            return

        def cb(done, total):
            self.root.after(0, lambda: self._update(done, total))

        self.root.after(0, lambda: self.status.config(text="翻訳中..."))

        self.processor.run(self.translator, cb)

        self.root.after(0, lambda: messagebox.showinfo("完了", "翻訳が完了しました"))
        self.root.after(0, lambda: self.status.config(text="完了"))

    def _update(self, done, total):
        if total == 0:
            return

        self.progress["value"] = (done / total) * 100
        self.status.config(text=f"{done}/{total}")

    def translation_history(self):
        history = self.translator.get_history()

        win = tk.Toplevel(self.root)
        win.title("翻訳履歴 / プレビュー")
        win.geometry("900x520")

        columns = ("source", "result", "engine")

        tree = ttk.Treeview(win, columns=columns, show="headings")
        tree.heading("source", text="原文")
        tree.heading("result", text="翻訳結果")
        tree.heading("engine", text="エンジン")

        tree.column("source", width=300)
        tree.column("result", width=380)
        tree.column("engine", width=100)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for item in history:
            tree.insert(
                "",
                "end",
                values=(
                    item.get("source", ""),
                    item.get("result", ""),
                    item.get("engine", ""),
                )
            )

        btn = ttk.Frame(win)
        btn.pack(pady=8)

        def retranslate_selected():
            selected = tree.selection()

            if not selected:
                messagebox.showinfo("再翻訳", "項目を選択してください")
                return

            item_id = selected[0]
            values = tree.item(item_id, "values")
            source = values[0]

            if not source:
                return

            try:
                result = self.translator.retranslate(source)
                tree.item(item_id, values=(source, result, "retranslate"))
                messagebox.showinfo("再翻訳", "再翻訳しました")
            except Exception as e:
                messagebox.showerror("再翻訳エラー", str(e))

        def clear_history():
            if messagebox.askyesno("確認", "翻訳履歴をクリアしますか？"):
                self.translator.clear_history()
                for i in tree.get_children():
                    tree.delete(i)

        ttk.Button(btn, text="選択項目を再翻訳", command=retranslate_selected).grid(row=0, column=0, padx=5)
        ttk.Button(btn, text="履歴クリア", command=clear_history).grid(row=0, column=1, padx=5)

    def settings(self):
        win = tk.Toplevel(self.root)
        win.title("設定")
        win.geometry("320x170")

        var = tk.StringVar(value=self.translator.config.get("model"))

        ttk.Label(win, text="モデル").pack(pady=8)
        ttk.Entry(win, textvariable=var, width=32).pack()

        def save():
            self.translator.config.set("model", var.get())
            messagebox.showinfo("OK", "保存しました")
            win.destroy()

        ttk.Button(win, text="保存", command=save).pack(pady=12)

    def logs(self):
        win = tk.Toplevel(self.root)
        win.title("ログ")
        win.geometry("700x450")

        text = tk.Text(win)
        text.pack(fill="both", expand=True)

        log_path = os.path.join(base_path(), "logs/app.log")

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                text.insert("end", f.read())
        except Exception:
            text.insert("end", "ログなし")

    def _check_update_startup(self):
        def run():
            try:
                res = self.updater.check_update()
                if res.get("update"):
                    self.root.after(0, lambda: self._ask_update(res))
            except Exception:
                pass

        threading.Thread(target=run, daemon=True).start()

    def manual_update(self):
        try:
            res = self.updater.check_update()

            if res.get("update"):
                self._ask_update(res)
            else:
                messagebox.showinfo("更新", "最新です")
        except Exception as e:
            messagebox.showerror("更新", f"確認に失敗しました\n{e}")

    def _ask_update(self, res):
        if messagebox.askyesno("アップデート", f"新バージョン {res['version']} を適用しますか？"):
            path = self.updater.download(res["url"])

            if path and self.updater.apply_update(path):
                messagebox.showinfo("完了", "更新完了。再起動してください")
            else:
                messagebox.showerror("エラー", "更新失敗")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()