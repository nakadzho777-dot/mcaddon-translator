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
        self.root.geometry("600x320")

        # =========================
        # Core
        # =========================
        self.translator = Translator()
        self.processor = MCAddonProcessor()
        self.updater = Updater(version="1.0.0")
        self.license = LicenseManager()

        # =========================
        # ライセンス（最初に必ず通す）
        # =========================
        if not self._license_gate():
            self.root.destroy()
            return

        # =========================
        # UI
        # =========================
        self._build_ui()

        # 起動時アップデート
        self._check_update_startup()

    # =========================================================
    # ライセンス認証（ゲート）
    # =========================================================

    def _license_gate(self):

        win = tk.Toplevel(self.root)
        win.title("ライセンス認証")
        win.geometry("320x160")
        win.resizable(False, False)

        tk.Label(win, text="ライセンスキーを入力").pack(pady=10)

        entry = tk.Entry(win, width=30)
        entry.pack()

        result = {"ok": False}

        def verify():

            key = entry.get().strip()

            if self.license.verify(key):
                result["ok"] = True
                win.destroy()
            else:
                messagebox.showerror("エラー", "ライセンスが無効です")
                self.root.destroy()

        tk.Button(win, text="認証", command=verify).pack(pady=10)

        win.transient(self.root)
        win.grab_set()
        self.root.wait_window(win)

        return result["ok"]

    # =========================================================
    # UI構築
    # =========================================================

    def _build_ui(self):

        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.progress = ttk.Progressbar(frame, length=500)
        self.progress.pack(pady=5)

        self.status = ttk.Label(frame, text="待機中")
        self.status.pack()

        btn = ttk.Frame(frame)
        btn.pack(pady=10)

        ttk.Button(btn, text="翻訳開始", command=self.run).grid(row=0, column=0, padx=5)
        ttk.Button(btn, text="設定", command=self.settings).grid(row=0, column=1, padx=5)
        ttk.Button(btn, text="ログ", command=self.logs).grid(row=0, column=2, padx=5)
        ttk.Button(btn, text="更新確認", command=self.manual_update).grid(row=0, column=3, padx=5)

    # =========================================================
    # 翻訳処理
    # =========================================================

    def run(self):

        path = filedialog.askdirectory()
        if not path:
            return

        threading.Thread(target=self._job, args=(path,), daemon=True).start()

    def _job(self, path):

        files = self.processor.scan(path)

        if not files:
            self.root.after(0, lambda: messagebox.showinfo("Info", "対象なし"))
            return

        def cb(done, total):
            self.root.after(0, lambda: self._update(done, total))

        self.processor.run(self.translator, cb)

        self.root.after(0, lambda: messagebox.showinfo("完了", "終了"))

    # =========================================================
    # 進捗
    # =========================================================

    def _update(self, done, total):

        if total == 0:
            return

        self.progress["value"] = (done / total) * 100
        self.status.config(text=f"{done}/{total}")

    # =========================================================
    # 設定
    # =========================================================

    def settings(self):

        win = tk.Toplevel(self.root)
        win.title("設定")
        win.geometry("300x150")

        var = tk.StringVar(value=self.translator.config.get("model"))

        ttk.Label(win, text="モデル").pack(pady=5)
        ttk.Entry(win, textvariable=var).pack()

        def save():
            self.translator.config.set("model", var.get())
            messagebox.showinfo("OK", "保存しました")

        ttk.Button(win, text="保存", command=save).pack(pady=10)

    # =========================================================
    # ログ
    # =========================================================

    def logs(self):

        win = tk.Toplevel(self.root)
        win.title("ログ")
        win.geometry("600x400")

        text = tk.Text(win)
        text.pack(fill="both", expand=True)

        log_path = os.path.join(base_path(), "logs/app.log")

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                text.insert("end", f.read())
        except:
            text.insert("end", "ログなし")

    # =========================================================
    # アップデート
    # =========================================================

    def _check_update_startup(self):

        def run():

            res = self.updater.check_update()

            if res.get("update"):
                self.root.after(0, lambda: self._ask_update(res))

        threading.Thread(target=run, daemon=True).start()

    def manual_update(self):

        res = self.updater.check_update()

        if res.get("update"):
            self._ask_update(res)
        else:
            messagebox.showinfo("更新", "最新です")

    def _ask_update(self, res):

        if messagebox.askyesno(
            "アップデート",
            f"新バージョン {res['version']} を適用しますか？"
        ):

            path = self.updater.download(res["url"])

            if path and self.updater.apply_update(path):
                messagebox.showinfo("完了", "更新完了。再起動してください")
            else:
                messagebox.showerror("エラー", "更新失敗")


# =========================================================
# 起動
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()