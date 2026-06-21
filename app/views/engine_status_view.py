import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from core.engine_setup import (
    is_argos_installed,
    is_ollama_installed,
    install_argos_full,
    open_ollama_download,
)


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#00e5ff"
WARN = "#facc15"
OK = "#9bef28"


class EngineStatusView:
    def __init__(self, parent, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.on_log = on_log
        self.style_prefix = style_prefix
        self.install_progress = None
        self.install_status = None

    def open(self):
        win = tk.Toplevel(self.parent)
        win.title("AIエンジン状態")
        win.geometry("840x680")
        win.minsize(780, 600)
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="AI ENGINE STATUS",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        main = self._card(win)
        main.pack(fill="both", expand=True, padx=16, pady=10)

        progress_panel = tk.Frame(main, bg=GLASS_DARK, highlightthickness=1, highlightbackground=ACCENT, bd=0)
        progress_panel.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(
            progress_panel,
            text="AI DOWNLOAD / SETUP PROGRESS",
            bg=GLASS_DARK,
            fg=ACCENT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=12, pady=(8, 3))

        self.install_status = tk.Label(
            progress_panel,
            text="待機中",
            bg=GLASS_DARK,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        )
        self.install_status.pack(anchor="w", padx=12, pady=(0, 4))

        self.install_progress = ttk.Progressbar(progress_panel, mode="indeterminate")
        self.install_progress.pack(fill="x", padx=12, pady=(0, 10))

        canvas = tk.Canvas(main, bg=GLASS, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=GLASS)

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=(0, 8))
        scrollbar.pack(side="right", fill="y", pady=(0, 8))

        self._engine_row(
            content,
            title="Argos Translate",
            desc="無料・オフライン翻訳。Free版の標準エンジン向け。",
            ready=is_argos_installed(),
            install_text="Argosをインストール",
            install_command=lambda: self._confirm_install_argos(win)
        )

        self._engine_row(
            content,
            title="Ollama",
            desc="無料・ローカルAI。Pro版の無料高品質モード向け。",
            ready=is_ollama_installed(),
            install_text="Ollama公式サイトを開く",
            install_command=lambda: self._confirm_open_ollama()
        )

        env = self._load_env()

        self._api_row(
            content,
            title="OpenAI API",
            desc="有料・高品質。利用者自身のAPIキーで使用。",
            key_exists=bool(env.get("OPENAI_API_KEY")),
            url="https://openai.com/api/pricing/"
        )

        self._api_row(
            content,
            title="OpenRouter API",
            desc="有料・モデル選択式。利用者自身のAPIキーで使用。",
            key_exists=bool(env.get("OPENROUTER_API_KEY")),
            url="https://openrouter.ai/pricing"
        )

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=16, pady=(0, 14))

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

    def _engine_row(self, parent, title, desc, ready, install_text, install_command):
        row = tk.Frame(parent, bg=GLASS_DARK, highlightthickness=1, highlightbackground=ACCENT, bd=0)
        row.pack(fill="x", padx=16, pady=8)

        left = tk.Frame(row, bg=GLASS_DARK)
        left.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        status = "✓ Ready" if ready else "⚠ インストール必要あり"
        color = OK if ready else WARN

        tk.Label(left, text=title, bg=GLASS_DARK, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(left, text=desc, bg=GLASS_DARK, fg=SUB, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 3))
        tk.Label(left, text=status, bg=GLASS_DARK, fg=color, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        ttk.Button(
            row,
            text=install_text,
            command=install_command,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=12, pady=12)

    def _api_row(self, parent, title, desc, key_exists, url):
        row = tk.Frame(parent, bg=GLASS_DARK, highlightthickness=1, highlightbackground=ACCENT, bd=0)
        row.pack(fill="x", padx=16, pady=8)

        status = "✓ APIキー設定済み" if key_exists else "⚠ APIキー未設定"
        color = OK if key_exists else WARN

        tk.Label(row, text=title, bg=GLASS_DARK, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 1))
        tk.Label(row, text=desc, bg=GLASS_DARK, fg=SUB, font=("Segoe UI", 9)).pack(anchor="w", padx=14)
        tk.Label(row, text=status, bg=GLASS_DARK, fg=color, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(3, 1))

        link = tk.Label(
            row,
            text=f"料金URL: {url}",
            bg=GLASS_DARK,
            fg=ACCENT,
            font=("Segoe UI", 9, "underline"),
            cursor="hand2"
        )
        link.pack(anchor="w", padx=14, pady=(0, 10))
        link.bind("<Button-1>", lambda e: webbrowser.open(url))

    def _confirm_install_argos(self, win):
        if is_argos_installed():
            messagebox.showinfo("Argos", "Argos Translate は既にインストールされています。")
            return

        ok = messagebox.askyesno(
            "確認",
            "Argos Translate をインストールしますか？\n\n"
            "無料で使えますが、ライブラリと英語→日本語モデルのダウンロードが必要です。\n"
            "インストール中は進捗バーを表示します。"
        )

        if not ok:
            return

        progress_win = self._open_install_progress_window("Argos Translate インストール中")
        self._set_install_progress("Argos Translate をインストール中...", True)
        self._log("⬇ Argos Translate インストール開始")

        def job():
            try:
                install_argos_full()
                win.after(0, lambda: self._set_install_progress("完了", False))
                win.after(0, lambda: self._close_progress_window(progress_win))
                win.after(0, lambda: messagebox.showinfo("完了", "Argos Translate のインストールが完了しました。\nアプリを再起動すると反映されます。"))
                self._log("✓ Argos Translate インストール完了")
            except Exception as e:
                guide = self._format_install_error(e)
                win.after(0, lambda: self._set_install_progress("失敗", False))
                win.after(0, lambda: self._close_progress_window(progress_win))
                win.after(0, lambda: messagebox.showerror("インストール失敗", guide))
                self._log(f"❌ Argos インストール失敗: {e}")

        threading.Thread(target=job, daemon=True).start()

    def _confirm_open_ollama(self):
        if is_ollama_installed():
            messagebox.showinfo("Ollama", "Ollama は既にインストールされています。")
            return

        ok = messagebox.askyesno(
            "確認",
            "Ollama公式ダウンロードページを開きますか？\n\nhttps://ollama.com/download"
        )

        if ok:
            self._set_install_progress("Ollama公式サイトを開きました。インストール後に再起動してください。", False)
            open_ollama_download()
            self._log("🌐 Ollama ダウンロードページを開きました")

    def _open_install_progress_window(self, title):
        win = tk.Toplevel(self.parent)
        win.title(title)
        win.geometry("520x170")
        win.configure(bg=DARK)
        win.resizable(False, False)

        tk.Label(
            win,
            text=title,
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 8))

        tk.Label(
            win,
            text="完了までこのままお待ちください。ネット接続が必要です。",
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=18, pady=(0, 8))

        bar = ttk.Progressbar(win, mode="indeterminate")
        bar.pack(fill="x", padx=18, pady=(4, 12))
        bar.start(10)
        win._install_bar = bar
        return win

    def _close_progress_window(self, win):
        try:
            if hasattr(win, "_install_bar"):
                win._install_bar.stop()
            win.destroy()
        except Exception:
            pass

    def _format_install_error(self, error):
        text = str(error)
        lower = text.lower()

        if "no module named pip" in lower or "pip" in lower and "not found" in lower:
            reason = "pip が見つかりません。Pythonのインストール状態を確認してください。"
        elif "permission" in lower or "access is denied" in lower or "winerror 5" in lower:
            reason = "権限不足の可能性があります。管理者として実行するか、ユーザー権限でインストールできるPython環境を使ってください。"
        elif "urlopen" in lower or "getaddrinfo" in lower or "timed out" in lower or "temporary failure" in lower:
            reason = "インターネット接続、DNS、またはダウンロード先への接続に失敗しています。"
        elif "model" in lower or "package" in lower:
            reason = "英語→日本語モデルのダウンロードまたは導入に失敗しました。"
        else:
            reason = "原因を自動判定できませんでした。エラー内容を確認してください。"

        return (
            "Argos Translate のインストールに失敗しました。\n\n"
            f"原因候補:\n{reason}\n\n"
            f"詳細:\n{text}\n\n"
            "無料で使いたい場合は、ネット接続を確認してから再試行してください。"
        )

    def _set_install_progress(self, text, running):
        if self.install_status:
            self.install_status.config(text=text)
        if self.install_progress:
            if running:
                self.install_progress.start(10)
            else:
                self.install_progress.stop()

    def _load_env(self):
        values = {}

        if not os.path.exists(".env"):
            return values

        with open(".env", "r", encoding="utf-8", errors="ignore") as f:
            for line in f.read().splitlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()

        return values

    def _card(self, parent):
        return tk.Frame(parent, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT, bd=0)

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)
