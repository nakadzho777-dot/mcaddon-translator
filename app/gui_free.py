import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_FILES = None
    TkinterDnD = None
    DND_AVAILABLE = False

from core.translator import Translator
from core.processor import MCAddonProcessor
from app.views.engine_status_view import EngineStatusView
from app.controllers.free_feature_controller import FreeFeatureController
from app.menu_config import FREE_MENU


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
BUTTON_DARK = "#0f2138"
ACCENT = "#9bef28"


class FreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MCAddon Translator FREE")
        self.root.geometry("1280x760")
        self.root.configure(bg=DARK)

        # 起動直後に最大化する（サイズ変更は可能）
        self.root.after(100, self._maximize_window)

        self.bg_original = None
        self.bg_photo = None
        self.bg_label = None
        self.resize_after_id = None

        self.translator = Translator()
        self.processor = MCAddonProcessor()

        self._style()
        self._load_background()
        self._init_views()
        self._build_ui()

        self.root.bind("<Configure>", self._on_resize)

    def _maximize_window(self):
        try:
            self.root.state("zoomed")
        except Exception:
            pass

        # 最大化で起動するが、ユーザーが必要に応じてサイズ変更できるようにする
        self.root.resizable(True, True)
        self.root.minsize(1100, 680)

        if self.bg_original:
            self._resize_background()

    def project_root(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def asset_path(self, filename):
        return os.path.join(self.project_root(), "assets", filename)

    def _init_views(self):
        self.features = FreeFeatureController(
            self.root,
            self.translator,
            self.processor,
            on_log=self.write_log,
            style_prefix="Free"
        )

    def _load_background(self):
        if Image is None or ImageTk is None:
            print("Pillow がありません: pip install pillow")
            return

        path = self.asset_path("bg_free.png")

        if not os.path.exists(path):
            print("背景画像なし:", path)
            return

        self.bg_original = Image.open(path).convert("RGB")
        self.bg_label = tk.Label(self.root, bd=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.after(200, self._resize_background)

    def _resize_background(self):
        if not self.bg_original or not self.bg_label:
            return

        self.root.update_idletasks()

        w = self.root.winfo_width()
        h = self.root.winfo_height()

        if w < 100:
            w = 1280
        if h < 100:
            h = 760

        img_w, img_h = self.bg_original.size
        scale = max(w / img_w, h / img_h)

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        resized = self.bg_original.resize((new_w, new_h), Image.LANCZOS)

        left = max(0, (new_w - w) // 2)
        top = max(0, (new_h - h) // 2)

        cropped = resized.crop((left, top, left + w, top + h))
        self.bg_photo = ImageTk.PhotoImage(cropped)

        self.bg_label.config(image=self.bg_photo)
        self.bg_label.lower()

    def _on_resize(self, event):
        if event.widget != self.root:
            return

        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)

        self.resize_after_id = self.root.after(120, self._resize_background)

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Free.Accent.TButton",
            background=ACCENT,
            foreground="#102000",
            bordercolor=ACCENT,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
            padding=12,
            font=("Segoe UI", 11, "bold")
        )

        style.map(
            "Free.Accent.TButton",
            background=[("active", "#bef264")]
        )

        style.configure(
            "Free.Dark.TButton",
            background=BUTTON_DARK,
            foreground=TEXT,
            bordercolor="#94a3b8",
            lightcolor=BUTTON_DARK,
            darkcolor=BUTTON_DARK,
            padding=10,
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Free.Dark.TButton",
            background=[("active", "#1e3a5f")],
            foreground=[("active", "#ffffff")]
        )

        style.configure(
            "Horizontal.TProgressbar",
            background=ACCENT,
            troughcolor="#172033",
            bordercolor="#94a3b8"
        )

    def card(self, parent, bg=GLASS, border=ACCENT):
        return tk.Frame(
            parent,
            bg=bg,
            highlightthickness=1,
            highlightbackground=border,
            bd=0
        )

    def label(self, parent, text, size=10, color=TEXT, bg=GLASS, bold=False):
        return tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal")
        )

    def _build_ui(self):
        self._build_drop_area()
        self._build_status_panel()
        self._build_action_panel()
        self._build_log_panel()
        self._write_welcome()
        self._enable_global_dnd()

    def _enable_global_dnd(self):
        if not DND_AVAILABLE:
            return

        targets = [self.root]

        if self.bg_label is not None:
            targets.append(self.bg_label)

        if hasattr(self, "drop_area"):
            targets.append(self.drop_area)

        for widget in targets:
            try:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self.on_drop)
            except Exception:
                pass

    def _build_drop_area(self):
        # ドロップ案内と進捗表示を同じ中央パネルに統合
        drop_card = self.card(self.root, bg=GLASS_DARK)
        drop_card.place(relx=0.30, rely=0.34, relwidth=0.38, relheight=0.16)

        self.drop_area = tk.Label(
            drop_card,
            text="✦ .mcaddon / .mcpack / .zip / フォルダをドロップ ✦\nFREE版で日本語化を開始",
            bg=GLASS_DARK,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold"),
            justify="center"
        )
        self.drop_area.pack(fill="x", expand=False, padx=10, pady=(10, 4))

        progress_row = tk.Frame(drop_card, bg=GLASS_DARK)
        progress_row.pack(fill="x", padx=18, pady=(0, 4))

        self.status = tk.Label(
            progress_row,
            text="待機中",
            bg=GLASS_DARK,
            fg=SUB,
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        )
        self.status.pack(side="left")

        self.progress_percent = tk.Label(
            progress_row,
            text="0%",
            bg=GLASS_DARK,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold"),
            anchor="e"
        )
        self.progress_percent.pack(side="right")

        self.progress = ttk.Progressbar(
            drop_card,
            mode="determinate",
            maximum=100
        )
        self.progress.pack(fill="x", padx=18, pady=(0, 10))

        if DND_AVAILABLE:
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind("<<Drop>>", self.on_drop)


    def _scrollable_card(self, relx, rely, relwidth, relheight, bg=GLASS, border=ACCENT):
        outer = self.card(self.root, bg=bg, border=border)
        outer.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)

        canvas = tk.Canvas(
            outer,
            bg=bg,
            highlightthickness=0,
            bd=0
        )
        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview
        )
        content = tk.Frame(canvas, bg=bg)

        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def on_content_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            try:
                if getattr(event, "num", None) == 4:
                    canvas.yview_scroll(-3, "units")
                elif getattr(event, "num", None) == 5:
                    canvas.yview_scroll(3, "units")
                else:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")
            except Exception:
                pass

        def enable_wheel(event=None):
            try:
                canvas.bind_all("<MouseWheel>", on_mousewheel)
                canvas.bind_all("<Button-4>", on_mousewheel)
                canvas.bind_all("<Button-5>", on_mousewheel)
            except Exception:
                pass

        def disable_wheel(event=None):
            try:
                canvas.unbind_all("<MouseWheel>")
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
            except Exception:
                pass

        def bind_recursive(widget):
            try:
                widget.bind("<Enter>", enable_wheel)
                widget.bind("<Leave>", disable_wheel)
            except Exception:
                pass
            for child in widget.winfo_children():
                bind_recursive(child)

        canvas.bind("<Enter>", enable_wheel)
        canvas.bind("<Leave>", disable_wheel)
        content.after(500, lambda: bind_recursive(content))

        return content

    def _build_status_panel(self):
        stats_card = self._scrollable_card(0.73, 0.20, 0.19, 0.20)

        self.label(stats_card, "FREE STATUS", size=12, bold=True).pack(anchor="w", padx=13, pady=(10, 6))

        self.translated_count = self._mini_stat(stats_card, "翻訳数", "0")
        self.ai_count = self._mini_stat(stats_card, "AI", "0")
        self.cache_count = self._mini_stat(stats_card, "CACHE", "0")

    def _build_action_panel(self):
        action_card = self._scrollable_card(0.73, 0.42, 0.19, 0.51)

        self.label(action_card, "FREE MENU", size=11, bold=True).pack(anchor="w", padx=13, pady=(10, 7))

        for text, method_name, kind in FREE_MENU:
            style = "Free.Accent.TButton" if kind == "accent" else "Free.Dark.TButton"
            if method_name.startswith("locked:"):
                feature_name = method_name.split(":", 1)[1]
                command = lambda name=feature_name: self.locked_feature(name)
            else:
                command = getattr(self, method_name)
            ttk.Button(action_card, text=text, command=command, style=style).pack(fill="x", padx=13, pady=3)


    def _build_log_panel(self):
        log_card = self.card(self.root)
        log_card.place(relx=0.05, rely=0.76, relwidth=0.52, relheight=0.14)

        self.label(log_card, "TRANSLATION LOG", size=11, bold=True).pack(anchor="w", padx=12, pady=(7, 2))

        self.log_text = tk.Text(
            log_card,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Consolas", 9),
            bd=0,
            height=4
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    def _mini_stat(self, parent, title, value):
        row = tk.Frame(parent, bg=GLASS)
        row.pack(fill="x", padx=13, pady=1)

        tk.Label(
            row,
            text=title,
            bg=GLASS,
            fg=SUB,
            font=("Segoe UI", 9, "bold"),
            width=10,
            anchor="w"
        ).pack(side="left")

        label = tk.Label(
            row,
            text=value,
            bg=GLASS,
            fg=ACCENT,
            font=("Segoe UI", 15, "bold")
        )
        label.pack(side="right")

        return label

    def _write_welcome(self):
        self.log_text.insert("end", "✨ MCAddon Translator FREE 起動\n")
        self.log_text.insert("end", "✓ .mcaddon / .mcpack / .zip 選択対応\n")
        self.log_text.insert("end", "✓ 画面全体D&D対応\n")
        self.log_text.insert("end", "✓ 基本翻訳モード\n\n")

    def normalize_drop_path(self, raw):
        path = raw.strip()

        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]

        return path

    def on_drop(self, event):
        path = self.normalize_drop_path(event.data)

        if os.path.exists(path):
            self.write_log(f"📦 ドロップ: {path}")
            threading.Thread(target=self._job, args=(path,), daemon=True).start()

    def write_log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def locked_feature(self, feature_name):
        self.features.locked_feature(feature_name)


    def select_input_path(self):
        path = filedialog.askopenfilename(
            title="翻訳するアドオンファイルを選択",
            filetypes=[
                ("Minecraft Addon / Pack", "*.mcaddon *.mcpack"),
                ("MCAddon", "*.mcaddon"),
                ("MCPack", "*.mcpack"),
                ("Zip", "*.zip"),
                ("All Files", "*.*"),
            ]
        )

        if path:
            return path

        folder = filedialog.askdirectory(
            title="または翻訳するフォルダを選択"
        )

        return folder

    def run(self):
        path = self.select_input_path()

        if path:
            self.write_log(f"📁 選択: {path}")
            threading.Thread(target=self._job, args=(path,), daemon=True).start()

    def _job(self, path):
        self.current_input_path = path
        self.root.after(0, lambda: self.write_log("📁 スキャン開始"))
        self.root.after(0, lambda: self.drop_area.config(text="翻訳準備中..."))
        self.root.after(0, lambda: self.status.config(text="スキャン中..."))
        self.root.after(0, lambda: self.progress.config(value=0))
        self.root.after(0, lambda: self.progress_percent.config(text="0%"))

        files = self.processor.scan(path)

        if not files:
            self.root.after(0, lambda: messagebox.showinfo("Info", "対象なし"))
            self.root.after(0, lambda: self.status.config(text="対象なし"))
            self.root.after(0, lambda: self.drop_area.config(text="対象ファイルが見つかりません"))
            self.root.after(0, lambda: self.progress_percent.config(text="0%"))
            return

        self.root.after(0, lambda: self.write_log(f"✅ 対象ファイル数: {len(files)}"))

        def cb(done, total):
            self.root.after(0, lambda: self._update(done, total))

        try:
            self.processor.run(self.translator, cb)
            self.root.after(0, self._finish)
        except Exception as e:
            self.root.after(0, lambda: self.write_log(f"❌ エラー: {e}"))
            self.root.after(0, self._discard_output_file)
            self.root.after(0, lambda: self.drop_area.config(text="エラーが発生しました\nAI設定を確認してください"))
            self.root.after(0, lambda: self.status.config(text="エラー"))
            self.root.after(0, lambda: self.progress.config(value=0))
            self.root.after(0, lambda: self.progress_percent.config(text="エラー"))
            self.root.after(0, lambda: self._show_ai_error_guide(str(e)))

    def _update(self, done, total):
        if total:
            percent = int((done / total) * 100)
            self.progress["value"] = percent
            self.progress_percent.config(text=f"{percent}%")
            self.drop_area.config(text="翻訳中...")
            self.status.config(text=f"翻訳中  {done}/{total}")
            self.translated_count.config(text=str(done))

    def update_stats(self):
        try:
            stats = self.translator.stats()
        except Exception:
            stats = {}

        self.ai_count.config(text=str(stats.get("ai", 0)))
        self.cache_count.config(text=str(stats.get("cache", 0)))

    def _finish(self):
        self.update_stats()

        issue = self._detect_ai_issue()
        if issue:
            self.write_log("⚠ 翻訳は完了扱いにしません。AI関連エラーを検出しました。")
            self._discard_output_file()
            self.status.config(text="エラー")
            self.drop_area.config(text="エラーが発生しました\nAI設定を確認してください")
            self.progress["value"] = 0
            self.progress_percent.config(text="エラー")
            self._show_ai_error_guide(issue)
            return

        self.write_log("🎉 翻訳完了")
        self.status.config(text="完了")
        self.drop_area.config(text="翻訳完了\n出力ファイルを開けます")
        self.progress["value"] = 100
        self.progress_percent.config(text="100%")

        if self.processor.output_path:
            self.write_log(f"📦 出力: {self.processor.output_path}")
            self._save_last_output(self.processor.output_path)

        if messagebox.askyesno("翻訳完了", "翻訳が完了しました。\n翻訳済みファイルを開きますか？"):
            self._open_output_file()

    def _discard_output_file(self):
        path = getattr(self.processor, "output_path", None)

        if not path:
            return

        try:
            if os.path.exists(path):
                os.remove(path)
                self.write_log(f"🗑 エラーのため出力ファイルを削除: {path}")
        except Exception as e:
            self.write_log(f"⚠ 出力ファイル削除に失敗: {e}")

    def _last_output_config_path(self):
        return os.path.join("data", "last_output.json")

    def _save_last_output(self, path):
        try:
            os.makedirs("data", exist_ok=True)
            with open(self._last_output_config_path(), "w", encoding="utf-8") as f:
                json.dump({"last_output": path}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.write_log(f"⚠ 最後の翻訳ファイル保存に失敗: {e}")

    def _load_last_output(self):
        try:
            path = self._last_output_config_path()
            if not os.path.exists(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            last = data.get("last_output")
            if last and os.path.exists(last):
                return last
            return None
        except Exception:
            return None

    def open_last_output(self):
        path = self._load_last_output()
        if not path:
            messagebox.showinfo("最後の翻訳", "最後に翻訳したファイルが見つかりません。")
            return
        try:
            os.startfile(path)
        except Exception:
            try:
                os.startfile(os.path.dirname(path))
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルを開けませんでした。\n{e}")

    def _open_output_file(self):
        path = getattr(self.processor, "output_path", None)

        if not path or not os.path.exists(path):
            return

        try:
            os.startfile(path)
        except Exception:
            try:
                os.startfile(os.path.dirname(path))
            except Exception:
                pass

    def _detect_ai_issue(self):
        try:
            stats = self.translator.stats()
            if stats.get("error", 0) <= 0:
                return None

            history = self.translator.get_history()
            joined = "\n".join(str(x.get("result", "")) for x in history[-30:])

            if "402" in joined or "Payment Required" in joined:
                return (
                    "AIサービスの料金不足、または支払い設定が必要です。\n\n"
                    "有料AIを使う場合は、AIエンジン状態画面から料金ページを開き、入金または支払い設定を行ってください。\n"
                    "無料で使いたい場合は、Argos または Ollama が使えます。Pro版では設定画面からAIを切り替えられます。"
                )

            if "OFFLINE" in joined or "Argos" in joined or "not installed" in joined.lower():
                return (
                    "AI翻訳エンジンが未導入、または利用できません。\n\n"
                    "無料で使いたい場合は、AIエンジン状態画面から Argos をインストールしてください。\n"
                    "Ollamaを使う場合は公式サイトからインストールできます。"
                )

            if "getaddrinfo" in joined or "URLError" in joined or "timeout" in joined.lower():
                return (
                    "AIサービスへの通信に失敗しました。\n\n"
                    "有料AIを使う場合は、APIキー・ネットワーク・料金状態を確認してください。\n"
                    "無料で使いたい場合は、Argos または Ollama を使う方法があります。"
                )

            return (
                "翻訳中にAI関連のエラーが発生しました。\n\n"
                "有料AIを使う場合は料金やAPIキーを確認してください。\n"
                "無料で使いたい場合は、AIエンジン状態画面から無料AIを準備できます。"
            )
        except Exception:
            return None

    def _show_ai_error_guide(self, message):
        self.write_log(f"⚠ AI設定確認: {message}")

        win = tk.Toplevel(self.root)
        win.title("AI設定が必要です")
        win.geometry("620x300")
        win.configure(bg=DARK)
        win.resizable(False, False)

        tk.Label(
            win,
            text="AI設定が必要です",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=18, pady=(16, 8))

        tk.Label(
            win,
            text=message,
            bg=DARK,
            fg=SUB,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=580
        ).pack(anchor="w", padx=18, pady=(0, 14))

        btns = tk.Frame(win, bg=DARK)
        btns.pack(fill="x", padx=18, pady=10)

        def open_settings():
            win.destroy()
            self.locked_feature("AIエンジン設定")

        def open_engine_status():
            win.destroy()
            EngineStatusView(
                self.root,
                on_log=self.write_log,
                style_prefix="Free"
            ).open()

        ttk.Button(
            btns,
            text="AIを変更する（Pro設定）",
            command=open_settings,
            style="Free.Accent.TButton"
        ).pack(fill="x", pady=4)

        ttk.Button(
            btns,
            text="インストール / 料金確認",
            command=open_engine_status,
            style="Free.Dark.TButton"
        ).pack(fill="x", pady=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style="Free.Dark.TButton"
        ).pack(fill="x", pady=4)

    def translation_rate(self):
        self.features.translation_rate()

    def update_check(self):
        self.features.update_check()


    def preview_limited(self):
        try:
            history = self.translator.get_history()
        except Exception:
            history = []

        latest = history[-1] if history else None

        win = tk.Toplevel(self.root)
        win.title("簡易プレビュー - FREE")
        win.geometry("760x460")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="FREE PREVIEW",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        box = tk.Text(
            win,
            bg=GLASS,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            wrap="word"
        )
        box.pack(fill="both", expand=True, padx=16, pady=8)

        if latest:
            box.insert("end", "【原文】\n")
            box.insert("end", latest.get("source", "") + "\n\n")
            box.insert("end", "【翻訳】\n")
            box.insert("end", latest.get("result", ""))
        else:
            box.insert("end", "まだ翻訳履歴がありません。")

        tk.Label(
            win,
            text="※ 履歴一覧・再翻訳・辞書登録はPro版機能です",
            bg=DARK,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 8))

    def show_help(self):
        messagebox.showinfo(
            "使い方",
            "1. .mcaddon / .mcpack / .zip / フォルダを用意\n"
            "2. 画面へドロップ、または翻訳開始を押す\n"
            "3. 翻訳完了後、出力ファイルを確認\n\n"
            "Free版は基本翻訳に特化しています。"
        )


if __name__ == "__main__":
    if DND_AVAILABLE and TkinterDnD:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    FreeApp(root)
    root.mainloop()