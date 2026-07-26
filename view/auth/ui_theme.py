"""Shared, dependency-free styling helpers for desktop windows."""

import tkinter as tk
from tkinter import ttk


class DesktopPalette:
    """Muted colors shared by authentication and lobby windows."""

    BACKGROUND = "#171a1f"
    SURFACE = "#22262d"
    SURFACE_RAISED = "#292e36"
    BORDER = "#3b424c"
    TEXT = "#f2f0e9"
    MUTED_TEXT = "#aeb4bd"
    ACCENT = "#b58a52"
    ACCENT_HOVER = "#c49a62"
    ACCENT_PRESSED = "#9d7443"
    ERROR = "#d98b83"
    SUCCESS = "#83b99a"
    INFO = "#8ea9c2"


def apply_desktop_theme(root: tk.Misc) -> ttk.Style:
    """Apply one consistent ttk theme without requiring platform assets."""
    palette = DesktopPalette
    root.configure(background=palette.BACKGROUND)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("App.TFrame", background=palette.BACKGROUND)
    style.configure(
        "Card.TFrame",
        background=palette.SURFACE,
        bordercolor=palette.BORDER,
        borderwidth=1,
        relief="solid",
    )
    style.configure(
        "Title.TLabel",
        background=palette.SURFACE,
        foreground=palette.TEXT,
        font=("Segoe UI", 22, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=palette.SURFACE,
        foreground=palette.MUTED_TEXT,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Field.TLabel",
        background=palette.SURFACE,
        foreground=palette.TEXT,
        font=("Segoe UI", 10, "bold"),
    )
    style.configure(
        "Body.TLabel",
        background=palette.SURFACE,
        foreground=palette.TEXT,
        font=("Segoe UI", 10),
    )
    for name, color in (
        ("Info", palette.INFO),
        ("Error", palette.ERROR),
        ("Success", palette.SUCCESS),
    ):
        style.configure(
            f"{name}.TLabel",
            background=palette.SURFACE_RAISED,
            foreground=color,
            font=("Segoe UI", 9),
            padding=(12, 9),
        )

    style.configure(
        "App.TEntry",
        fieldbackground=palette.SURFACE_RAISED,
        foreground=palette.TEXT,
        insertcolor=palette.TEXT,
        bordercolor=palette.BORDER,
        lightcolor=palette.BORDER,
        darkcolor=palette.BORDER,
        padding=(11, 9),
    )
    style.map(
        "App.TEntry",
        bordercolor=[("focus", palette.ACCENT)],
        lightcolor=[("focus", palette.ACCENT)],
        darkcolor=[("focus", palette.ACCENT)],
    )
    _configure_button(style, "Primary.TButton", palette.ACCENT, "#17130f")
    _configure_button(style, "Secondary.TButton", palette.SURFACE_RAISED, palette.TEXT)
    _configure_button(style, "Danger.TButton", palette.SURFACE_RAISED, palette.ERROR)
    return style


def _configure_button(
    style: ttk.Style,
    name: str,
    background: str,
    foreground: str,
) -> None:
    palette = DesktopPalette
    style.configure(
        name,
        background=background,
        foreground=foreground,
        borderwidth=0,
        focusthickness=1,
        focuscolor=palette.ACCENT,
        font=("Segoe UI", 10, "bold"),
        padding=(16, 10),
    )
    style.map(
        name,
        background=[
            ("disabled", palette.SURFACE),
            ("pressed", palette.ACCENT_PRESSED),
            ("active", palette.ACCENT_HOVER),
        ],
        foreground=[("disabled", "#686e76")],
    )


def fit_and_center(window: tk.Misc, minimum_width: int = 0) -> None:
    """Size a window to its requested content and center it on screen."""
    window.update_idletasks()
    width = max(window.winfo_reqwidth(), minimum_width)
    height = window.winfo_reqheight()
    x = max(0, (window.winfo_screenwidth() - width) // 2)
    y = max(0, (window.winfo_screenheight() - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

