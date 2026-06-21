import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


TEXT = "#f8fafc"
SUB = "#cbd5e1"
DARK = "#020617"
GLASS = "#07111f"
GLASS_DARK = "#030814"
ACCENT = "#00e5ff"


class DictionaryView:

    def __init__(
        self,
        parent,
        translator,
        on_log=None,
        on_stats_update=None,
        style_prefix="Launcher"
    ):
        self.parent = parent
        self.translator = translator
        self.on_log = on_log
        self.on_stats_update = on_stats_update
        self.style_prefix = style_prefix

        self.items = []

    def open(self):

        win = tk.Toplevel(self.parent)
        win.title("辞書編集")
        win.geometry("1100x680")
        win.configure(bg=DARK)

        tk.Label(
            win,
            text="USER DICTIONARY",
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
        search_entry.pack(fill="x", padx=10, pady=(10, 8))

        count_label = tk.Label(
            left,
            text="登録数: 0",
            bg=GLASS,
            fg=ACCENT,
            font=("Segoe UI", 10, "bold")
        )
        count_label.pack(anchor="w", padx=10)

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

        listbox.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(8, 10)
        )

        tk.Label(
            right,
            text="原文",
            bg=GLASS,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 3))

        source_entry = tk.Entry(
            right,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 11)
        )

        source_entry.pack(fill="x", padx=12)

        tk.Label(
            right,
            text="翻訳",
            bg=GLASS,
            fg=SUB,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 3))

        result_entry = tk.Entry(
            right,
            bg=GLASS_DARK,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 11)
        )

        result_entry.pack(fill="x", padx=12)

        current = {"key": None}

        def load_dictionary():

            self.items.clear()

            try:
                data = self._load_dictionary()

                for k, v in data.items():
                    self.items.append((k, v))

            except Exception:
                pass

            refresh()

        def refresh():

            listbox.delete(0, "end")

            query = search_var.get().lower().strip()

            count = 0

            for k, v in self.items:

                text = f"{k} {v}".lower()

                if query and query not in text:
                    continue

                listbox.insert("end", f"{k} → {v}")

                count += 1

            count_label.config(
                text=f"登録数: {count}"
            )

        def on_select(event=None):

            sel = listbox.curselection()

            if not sel:
                return

            idx = sel[0]

            query = search_var.get().lower().strip()

            filtered = []

            for k, v in self.items:

                text = f"{k} {v}".lower()

                if query and query not in text:
                    continue

                filtered.append((k, v))

            if idx >= len(filtered):
                return

            k, v = filtered[idx]

            current["key"] = k

            source_entry.delete(0, "end")
            result_entry.delete(0, "end")

            source_entry.insert(0, k)
            result_entry.insert(0, v)

        def add_word():

            source = source_entry.get().strip()
            result = result_entry.get().strip()

            if not source or not result:
                return

            self.translator.add_user_word(
                source,
                result
            )

            self._log(
                f"📘 辞書追加: {source}"
            )

            load_dictionary()
            self._stats()

        def update_word():

            old = current["key"]

            if not old:
                return

            source = source_entry.get().strip()
            result = result_entry.get().strip()

            data = self._load_dictionary()

            if old in data:
                del data[old]

            data[source] = result

            self._save_dictionary(data)

            self._log(
                f"✏ 辞書編集: {source}"
            )

            load_dictionary()
            self._stats()

        def delete_word():

            key = current["key"]

            if not key:
                return

            if not messagebox.askyesno(
                "確認",
                f"{key} を削除しますか？"
            ):
                return

            data = self._load_dictionary()

            if key in data:
                del data[key]

            self._save_dictionary(data)

            self._log(
                f"🗑 辞書削除: {key}"
            )

            load_dictionary()
            self._stats()

        def export_dictionary():

            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON", "*.json")]
            )

            if not path:
                return

            data = self._load_dictionary()

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            messagebox.showinfo(
                "完了",
                "エクスポートしました"
            )

        def import_dictionary():

            path = filedialog.askopenfilename(
                filetypes=[("JSON", "*.json")]
            )

            if not path:
                return

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            self._save_dictionary(data)

            load_dictionary()

            self._log(
                "📥 辞書インポート"
            )

        search_var.trace_add(
            "write",
            lambda *args: refresh()
        )

        listbox.bind(
            "<<ListboxSelect>>",
            on_select
        )

        btns = tk.Frame(
            right,
            bg=GLASS
        )

        btns.pack(
            fill="x",
            padx=12,
            pady=18
        )

        buttons = [
            ("追加", add_word),
            ("更新", update_word),
            ("削除", delete_word),
            ("インポート", import_dictionary),
            ("エクスポート", export_dictionary),
        ]

        for text, cmd in buttons:

            ttk.Button(
                btns,
                text=text,
                command=cmd,
                style=f"{self.style_prefix}.Dark.TButton"
            ).pack(
                side="left",
                padx=4
            )

        load_dictionary()

    def _dictionary_path(self):

        return os.path.join(
            "data",
            "user_dictionary.json"
        )

    def _load_dictionary(self):

        path = self._dictionary_path()

        if not os.path.exists(path):
            return {}

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    def _save_dictionary(self, data):

        path = self._dictionary_path()

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

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