import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

from app.views.engine_status_view import EngineStatusView


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#00e5ff"


ENGINE_INFO = {
    "argos": {
        "name": "Argos Translate",
        "price": "無料 / オフライン",
        "speed": "速い",
        "quality": "標準",
        "recommend": "Free版・大量翻訳・API代を使いたくない場合",
        "url": "",
        "note": "完全無料で使えます。未導入の場合はAIエンジン状態画面からインストールできます。"
    },
    "ollama": {
        "name": "Ollama",
        "price": "無料 / ローカル",
        "speed": "PC性能依存",
        "quality": "中〜高",
        "recommend": "Pro版の無料高品質モード",
        "url": "https://ollama.com/download",
        "note": "PCにOllama本体のインストールが必要です。AIエンジン状態画面から公式サイトを開けます。"
    },
    "openrouter": {
        "name": "OpenRouter",
        "price": "従量課金 / モデルごとに変動",
        "speed": "速い",
        "quality": "高",
        "recommend": "Pro版の高品質翻訳",
        "url": "https://openrouter.ai/pricing",
        "note": "利用者自身のOpenRouter APIキーを入力して使います。"
    },
    "openai": {
        "name": "OpenAI",
        "price": "従量課金 / モデルごとに変動",
        "speed": "速い",
        "quality": "高〜最高",
        "recommend": "Pro版の最高品質翻訳・AIレビュー",
        "url": "https://openai.com/api/pricing/",
        "note": "利用者自身のOpenAI APIキーを入力して使います。"
    }
}


class SettingsView:
    def __init__(self, parent, on_log=None, style_prefix="Launcher"):
        self.parent = parent
        self.on_log = on_log
        self.style_prefix = style_prefix

    def open(self):
        config = self._load_config()
        env = self._load_env_values()

        win = tk.Toplevel(self.parent)
        win.title("設定")
        win.geometry("860x600")
        win.minsize(720, 480)
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="SETTINGS",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 6))

        body = tk.Frame(win, bg=DARK)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        canvas = tk.Canvas(body, bg=DARK, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=DARK)
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def on_content_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)

        def on_mousewheel(event):
            if getattr(event, "num", None) == 4:
                canvas.yview_scroll(-3, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(3, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")

        def bind_wheel(widget):
            widget.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
            widget.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
            widget.bind("<Button-4>", on_mousewheel)
            widget.bind("<Button-5>", on_mousewheel)
            for child in widget.winfo_children():
                bind_wheel(child)

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        main = self._card(content)
        main.pack(fill="both", expand=True)

        engine_var = tk.StringVar(value=config.get("engine", env.get("TRANSLATE_ENGINE", "argos")))
        openai_key_var = tk.StringVar(value=env.get("OPENAI_API_KEY", ""))
        openrouter_key_var = tk.StringVar(value=env.get("OPENROUTER_API_KEY", ""))
        openai_model_var = tk.StringVar(value=config.get("model", env.get("OPENAI_MODEL", "gpt-4o-mini")))
        openrouter_model_var = tk.StringVar(value=config.get("openrouter_model", env.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")))
        ollama_model_var = tk.StringVar(value=config.get("ollama_model", env.get("OLLAMA_MODEL", "gemma3")))
        speed_var = tk.StringVar(value=config.get("speed", "normal"))
        log_save_var = tk.BooleanVar(value=config.get("save_logs", True))
        auto_preview_var = tk.BooleanVar(value=config.get("auto_preview", False))
        theme_var = tk.StringVar(value=config.get("theme", "glass_launcher"))

        self._section(main, "AI ENGINE")

        top = tk.Frame(main, bg=GLASS)
        top.pack(fill="x", padx=16, pady=(0, 8))

        left = tk.Frame(top, bg=GLASS)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(top, bg=GLASS_DARK, highlightthickness=1, highlightbackground=ACCENT, bd=0)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self._row_label(left, "翻訳エンジン")
        ttk.Combobox(left, textvariable=engine_var, values=["argos", "ollama", "openrouter", "openai"], state="readonly").pack(fill="x", pady=(0, 8))

        ttk.Button(left, text="AIエンジン状態を確認", command=self.open_engine_status, style=f"{self.style_prefix}.Dark.TButton").pack(fill="x", pady=(0, 12))

        self._row_label(left, "OpenAI API Key")
        tk.Entry(left, textvariable=openai_key_var, show="*", bg=GLASS_DARK, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10)).pack(fill="x", pady=(0, 8))

        self._row_label(left, "OpenRouter API Key")
        tk.Entry(left, textvariable=openrouter_key_var, show="*", bg=GLASS_DARK, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10)).pack(fill="x", pady=(0, 8))

        self._row_label(left, "OpenAIモデル")
        tk.Entry(left, textvariable=openai_model_var, bg=GLASS_DARK, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10)).pack(fill="x", pady=(0, 8))

        self._row_label(left, "OpenRouterモデル")
        tk.Entry(left, textvariable=openrouter_model_var, bg=GLASS_DARK, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10)).pack(fill="x", pady=(0, 8))

        self._row_label(left, "Ollamaモデル")
        tk.Entry(left, textvariable=ollama_model_var, bg=GLASS_DARK, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10)).pack(fill="x", pady=(0, 8))

        info_text = tk.Text(right, height=15, bg=GLASS_DARK, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 10), wrap="word")
        info_text.pack(fill="both", expand=True, padx=12, pady=12)

        def update_engine_info(*args):
            info = ENGINE_INFO.get(engine_var.get(), ENGINE_INFO["argos"])
            info_text.config(state="normal")
            info_text.delete("1.0", "end")
            info_text.insert("end", f"{info['name']}\n\n")
            info_text.insert("end", f"料金: {info['price']}\n")
            info_text.insert("end", f"速度: {info['speed']}\n")
            info_text.insert("end", f"品質: {info['quality']}\n")
            info_text.insert("end", f"おすすめ: {info['recommend']}\n\n")
            if info["url"]:
                info_text.insert("end", f"URL:\n{info['url']}\n\n")
            info_text.insert("end", info["note"])
            info_text.config(state="disabled")

        engine_var.trace_add("write", update_engine_info)
        update_engine_info()

        self._section(main, "BEHAVIOR")
        self._row_label(main, "翻訳速度")
        ttk.Combobox(main, textvariable=speed_var, values=["safe", "normal", "fast"], state="readonly").pack(fill="x", padx=16, pady=(0, 8))

        tk.Checkbutton(main, text="ログを保存する", variable=log_save_var, bg=GLASS, fg=TEXT, selectcolor=GLASS_DARK, activebackground=GLASS, activeforeground=TEXT, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=4)
        tk.Checkbutton(main, text="翻訳完了後にプレビューを自動表示", variable=auto_preview_var, bg=GLASS, fg=TEXT, selectcolor=GLASS_DARK, activebackground=GLASS, activeforeground=TEXT, font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=4)

        self._section(main, "THEME")
        self._row_label(main, "テーマ")
        ttk.Combobox(main, textvariable=theme_var, values=["pro_dark", "glass_launcher", "simple_dark"], state="readonly").pack(fill="x", padx=16, pady=(0, 16))

        button_bar = tk.Frame(win, bg=DARK)
        button_bar.pack(fill="x", padx=14, pady=(0, 12))

        def save():
            data = {
                "engine": engine_var.get(),
                "model": openai_model_var.get().strip(),
                "openrouter_model": openrouter_model_var.get().strip(),
                "ollama_model": ollama_model_var.get().strip(),
                "speed": speed_var.get(),
                "save_logs": bool(log_save_var.get()),
                "auto_preview": bool(auto_preview_var.get()),
                "theme": theme_var.get()
            }
            env_updates = {
                "TRANSLATE_ENGINE": engine_var.get(),
                "OPENAI_API_KEY": openai_key_var.get().strip(),
                "OPENAI_MODEL": openai_model_var.get().strip(),
                "OPENROUTER_API_KEY": openrouter_key_var.get().strip(),
                "OPENROUTER_MODEL": openrouter_model_var.get().strip(),
                "OLLAMA_MODEL": ollama_model_var.get().strip()
            }
            self._save_config(data)
            self._write_env_values(env_updates)
            self._log(f"⚙ 設定を保存しました: {engine_var.get()}")
            messagebox.showinfo("保存", "設定を保存しました。\n次の翻訳から再起動なしで反映されます。")

        ttk.Button(button_bar, text="保存", command=save, style=f"{self.style_prefix}.Dark.TButton").pack(side="left", padx=4)
        ttk.Button(button_bar, text="閉じる", command=win.destroy, style=f"{self.style_prefix}.Dark.TButton").pack(side="right", padx=4)

        content.after(500, lambda: bind_wheel(content))

    def open_engine_status(self):
        EngineStatusView(self.parent, on_log=self.on_log, style_prefix=self.style_prefix).open()

    def _section(self, parent, text):
        tk.Label(parent, text=text, bg=GLASS, fg=ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(14, 6))

    def _row_label(self, parent, text):
        tk.Label(parent, text=text, bg=GLASS, fg=SUB, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 3))

    def _card(self, parent):
        return tk.Frame(parent, bg=GLASS, highlightthickness=1, highlightbackground=ACCENT, bd=0)

    def _config_path(self):
        return os.path.join("data", "config.json")

    def _default_config(self):
        return {
            "engine": "argos",
            "model": "gpt-4o-mini",
            "openrouter_model": "openai/gpt-4o-mini",
            "ollama_model": "gemma3",
            "speed": "normal",
            "save_logs": True,
            "auto_preview": False,
            "theme": "glass_launcher"
        }

    def _load_config(self):
        path = self._config_path()
        if not os.path.exists(path):
            return self._default_config()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            default = self._default_config()
            default.update(data)
            return default
        except Exception:
            return self._default_config()

    def _save_config(self, data):
        os.makedirs("data", exist_ok=True)
        with open(self._config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_env_values(self):
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

    def _write_env_values(self, updates):
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()
        existing_keys = set()
        new_lines = []
        for line in lines:
            if "=" not in line:
                new_lines.append(line)
                continue
            key = line.split("=", 1)[0].strip()
            if key in updates:
                value = updates[key]
                if value != "":
                    new_lines.append(f"{key}={value}")
                existing_keys.add(key)
            else:
                new_lines.append(line)
        for key, value in updates.items():
            if key not in existing_keys and value != "":
                new_lines.append(f"{key}={value}")
        with open(env_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(new_lines) + "\n")

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)
