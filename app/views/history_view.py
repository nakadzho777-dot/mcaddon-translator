import tkinter as tk
from tkinter import ttk, messagebox


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#00e5ff"


class HistoryView:
    def __init__(
        self,
        parent,
        translator,
        preview_view=None,
        on_log=None,
        on_stats_update=None,
        style_prefix="Launcher"
    ):
        self.parent = parent
        self.translator = translator
        self.preview_view = preview_view
        self.on_log = on_log
        self.on_stats_update = on_stats_update
        self.style_prefix = style_prefix

    def open(self):
        history = self._safe_history()

        win = tk.Toplevel(self.parent)
        win.title("翻訳履歴")
        win.geometry("1080x640")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="TRANSLATION HISTORY",
            bg=DARK,
            fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 8))

        main = tk.Frame(win, bg=DARK)
        main.pack(fill="both", expand=True, padx=16, pady=10)

        left = self._card(main)
        left.pack(side="left", fill="y", padx=(0, 10))

        right = self._card(main)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(
            left,
            text=f"履歴一覧  {len(history)} 件",
            bg=GLASS,
            fg=TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        search_var = tk.StringVar()

        search_entry = tk.Entry(
            left,
            textvariable=search_var,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10)
        )
        search_entry.pack(fill="x", padx=10, pady=(0, 8))
        search_entry.insert(0, "")

        listbox = tk.Listbox(
            left,
            width=38,
            bg=GLASS_DARK,
            fg=TEXT,
            selectbackground=ACCENT,
            selectforeground="#001018",
            relief="flat",
            font=("Segoe UI", 10)
        )
        listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(
            right,
            text="原文",
            bg=GLASS,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 3))

        source_box = tk.Text(
            right,
            height=8,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            wrap="word"
        )
        source_box.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        tk.Label(
            right,
            text="翻訳結果",
            bg=GLASS,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(3, 3))

        result_box = tk.Text(
            right,
            height=8,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            wrap="word"
        )
        result_box.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        filtered = []
        current = {"index": None}

        def make_label(i, item):
            src = item.get("source", "").replace("\n", " ")
            res = item.get("result", "").replace("\n", " ")

            if len(src) > 28:
                src = src[:28] + "..."

            if len(res) > 18:
                res = res[:18] + "..."

            return f"{i + 1}. {src} → {res}"

        def refresh_list():
            listbox.delete(0, "end")
            filtered.clear()

            q = search_var.get().strip().lower()

            for i, item in enumerate(history):
                src = item.get("source", "")
                res = item.get("result", "")
                text = f"{src} {res}".lower()

                if q and q not in text:
                    continue

                filtered.append((i, item))
                listbox.insert("end", make_label(i, item))

            if filtered:
                listbox.selection_set(len(filtered) - 1)
                listbox.see(len(filtered) - 1)
                load_selected()
            else:
                current["index"] = None
                source_box.delete("1.0", "end")
                result_box.delete("1.0", "end")
                source_box.insert("end", "該当する履歴がありません。")

        def load_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return

            real_index, item = filtered[sel[0]]
            current["index"] = real_index

            source_box.delete("1.0", "end")
            result_box.delete("1.0", "end")

            source_box.insert("end", item.get("source", ""))
            result_box.insert("end", item.get("result", ""))

        listbox.bind("<<ListboxSelect>>", load_selected)

        def on_search(*args):
            refresh_list()

        search_var.trace_add("write", on_search)

        btns = tk.Frame(right, bg=GLASS)
        btns.pack(fill="x", padx=12, pady=(0, 12))

        def selected_item():
            idx = current.get("index")
            if idx is None:
                messagebox.showinfo("Info", "履歴を選択してください")
                return None
            return history[idx]

        def open_preview():
            item = selected_item()
            if not item:
                return

            if self.preview_view:
                self.preview_view.open(item)
            else:
                messagebox.showinfo("Info", "プレビュー画面が接続されていません")

        def retranslate_selected():
            source = source_box.get("1.0", "end").strip()

            if not source:
                messagebox.showinfo("Info", "原文が空です")
                return

            result = self.translator.retranslate(source)

            result_box.delete("1.0", "end")
            result_box.insert("end", result)

            self._stats()
            self._log("🔁 履歴から再翻訳")

        def add_dict_selected():
            source = source_box.get("1.0", "end").strip()
            result = result_box.get("1.0", "end").strip()

            if not source or not result:
                messagebox.showinfo("Info", "原文と翻訳結果を入力してください")
                return

            self.translator.add_user_word(source, result)
            self._stats()
            self._log("📘 履歴から辞書登録")
            messagebox.showinfo("辞書登録", "ユーザー辞書に登録しました")

        ttk.Button(
            btns,
            text="プレビューで開く",
            command=open_preview,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="再翻訳",
            command=retranslate_selected,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="辞書登録",
            command=add_dict_selected,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            btns,
            text="閉じる",
            command=win.destroy,
            style=f"{self.style_prefix}.Dark.TButton"
        ).pack(side="right", padx=4)

        if history:
            refresh_list()
        else:
            source_box.insert("end", "まだ翻訳履歴がありません。")
            result_box.insert("end", "翻訳後にここへ履歴が表示されます。")

    def _safe_history(self):
        try:
            history = self.translator.get_history()
            if isinstance(history, list):
                return history
        except Exception:
            pass
        return []

    def _card(self, parent):
        return tk.Frame(
            parent,
            bg=GLASS,
            highlightthickness=1,
            highlightbackground=ACCENT,
            bd=0
        )

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)

    def _stats(self):
        if self.on_stats_update:
            self.on_stats_update()