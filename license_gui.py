import tkinter as tk
from core.license import activate_license


class LicenseWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)

        self.title("ライセンス認証")
        self.geometry("320x160")

        self.on_success = on_success

        tk.Label(self, text="ライセンスキーを入力").pack(pady=10)

        self.entry = tk.Entry(self, width=30)
        self.entry.pack(pady=5)

        tk.Button(self, text="認証", command=self.check).pack(pady=5)

        self.label = tk.Label(self, text="")
        self.label.pack(pady=5)

    def check(self):
        key = self.entry.get().strip()

        success, msg = activate_license(key)

        self.label.config(text=msg)

        if success:
            self.after(1000, self.finish)

    def finish(self):
        self.on_success()
        self.destroy()