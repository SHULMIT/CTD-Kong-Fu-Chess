"""Themed modal text prompt used by multiplayer menus."""

import tkinter as tk
from tkinter import ttk

from view.auth.ui_theme import apply_desktop_theme, fit_and_center


def ask_text(
    parent: tk.Misc,
    title: str,
    message: str,
    *,
    initial_focus: bool = True,
) -> str | None:
    """Display a compact themed prompt and return trimmed input or ``None``."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(parent)
    apply_desktop_theme(dialog)
    result: list[str | None] = [None]
    value = tk.StringVar()

    outer = ttk.Frame(dialog, style="App.TFrame", padding=16)
    outer.grid(sticky="nsew")
    card = ttk.Frame(outer, style="Card.TFrame", padding=24)
    card.grid(sticky="nsew")
    card.columnconfigure(0, weight=1)
    ttk.Label(card, text=title, style="Title.TLabel").grid(sticky="w")
    ttk.Label(
        card,
        text=message,
        style="Subtitle.TLabel",
        wraplength=440,
        justify="left",
    ).grid(row=1, sticky="ew", pady=(8, 18))
    entry = ttk.Entry(card, textvariable=value, style="App.TEntry", width=42)
    entry.grid(row=2, sticky="ew")
    actions = ttk.Frame(card, style="Card.TFrame")
    actions.grid(row=3, sticky="e", pady=(20, 0))

    def close(submit: bool = False) -> None:
        text = value.get().strip()
        result[0] = text if submit and text else None
        dialog.destroy()

    ttk.Button(
        actions, text="Cancel", style="Secondary.TButton", command=close
    ).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(
        actions,
        text="Continue",
        style="Primary.TButton",
        command=lambda: close(True),
    ).grid(row=0, column=1)
    dialog.bind("<Return>", lambda _event: close(True))
    dialog.bind("<Escape>", lambda _event: close())
    dialog.protocol("WM_DELETE_WINDOW", close)
    fit_and_center(dialog, 420)
    dialog.grab_set()
    if initial_focus:
        entry.focus_set()
    parent.wait_window(dialog)
    return result[0]
