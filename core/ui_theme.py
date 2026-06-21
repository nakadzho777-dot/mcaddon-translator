import tkinter as tk
from tkinter import ttk


BG_DARK = "#0f172a"
BG_CARD = "#111827"
BG_SOFT = "#1e293b"
TEXT_MAIN = "#f8fafc"
TEXT_SUB = "#cbd5e1"
ACCENT = "#38bdf8"
ACCENT_GREEN = "#22c55e"
WARNING = "#f97316"


def apply_theme(root):
    root.configure(bg=BG_DARK)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TFrame",
        background=BG_DARK
    )

    style.configure(
        "Card.TFrame",
        background=BG_CARD,
        relief="flat"
    )

    style.configure(
        "TLabel",
        background=BG_DARK,
        foreground=TEXT_MAIN,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Sub.TLabel",
        background=BG_DARK,
        foreground=TEXT_SUB,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Title.TLabel",
        background=BG_DARK,
        foreground=TEXT_MAIN,
        font=("Segoe UI", 18, "bold")
    )

    style.configure(
        "CardTitle.TLabel",
        background=BG_CARD,
        foreground=TEXT_MAIN,
        font=("Segoe UI", 12, "bold")
    )

    style.configure(
        "CardText.TLabel",
        background=BG_CARD,
        foreground=TEXT_SUB,
        font=("Segoe UI", 9)
    )

    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#020617",
        font=("Segoe UI", 10, "bold"),
        padding=8
    )

    style.map(
        "Accent.TButton",
        background=[("active", "#7dd3fc")]
    )

    style.configure(
        "Dark.TButton",
        background=BG_SOFT,
        foreground=TEXT_MAIN,
        font=("Segoe UI", 10),
        padding=8
    )

    style.map(
        "Dark.TButton",
        background=[("active", "#334155")]
    )

    style.configure(
        "Horizontal.TProgressbar",
        background=ACCENT,
        troughcolor=BG_SOFT,
        bordercolor=BG_SOFT,
        lightcolor=ACCENT,
        darkcolor=ACCENT
    )


def make_card(parent):
    frame = ttk.Frame(parent, style="Card.TFrame")
    return frame


def gradient_background(canvas, width, height):
    for i in range(height):
        r = int(15 + (30 - 15) * i / height)
        g = int(23 + (41 - 23) * i / height)
        b = int(42 + (59 - 42) * i / height)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)


def pro_badge(parent, text="PRO"):
    label = tk.Label(
        parent,
        text=text,
        bg=ACCENT_GREEN,
        fg="#052e16",
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=3
    )
    return label


def free_badge(parent, text="FREE"):
    label = tk.Label(
        parent,
        text=text,
        bg=BG_SOFT,
        fg=TEXT_SUB,
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=3
    )
    return label