"""Floating transparent overlay showing real-time partial transcription.

Uses a frameless tkinter window. Theme-aware colors from theme.py.
Rounded appearance via a padded inner frame.
"""

import logging
import threading
import tkinter as tk
from typing import Optional

from .fonts import FONT_FAMILY
from .settings import Settings
from .theme import get_colors, RADIUS_LG

log = logging.getLogger(__name__)

_PADDING_X = 18
_PADDING_Y = 10
_MARGIN = 60
_MIN_WIDTH = 300


class TranscriptionOverlay:
    """A small floating bar showing live transcription text."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._root: Optional[tk.Tk] = None
        self._label: Optional[tk.Label] = None
        self._status_dot: Optional[tk.Canvas] = None
        self._thread: Optional[threading.Thread] = None
        self._visible = False
        self._ready = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=3)

    def _get_theme_colors(self) -> tuple[str, str, str]:
        """Return (bg, fg, accent) based on current theme setting."""
        colors = get_colors(self._settings.theme)
        return colors.overlay_bg, colors.overlay_fg, colors.overlay_accent

    def _run_tk(self) -> None:
        bg, fg, accent = self._get_theme_colors()

        self._root = tk.Tk()
        self._root.title("Eqho")
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", self._settings.overlay_opacity)

        # Transparent root — the visual shape comes from the inner frame
        self._root.configure(bg=bg)

        frame = tk.Frame(self._root, bg=bg, padx=_PADDING_X, pady=_PADDING_Y)
        frame.pack(fill=tk.BOTH, expand=True)

        self._status_dot = tk.Canvas(
            frame, width=10, height=10, bg=bg, highlightthickness=0,
        )
        self._status_dot.create_oval(1, 1, 9, 9, fill=accent, outline="", tags="dot")
        self._status_dot.pack(side=tk.LEFT, padx=(0, 8))

        self._label = tk.Label(
            frame,
            text="Listening...",
            font=(FONT_FAMILY, self._settings.overlay_font_size),
            fg=fg,
            bg=bg,
            anchor="w",
            wraplength=600,
        )
        self._label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._root.withdraw()
        self._ready.set()
        self._root.mainloop()

    def show(self, text: str = "Listening...") -> None:
        if not self._settings.overlay_enabled:
            return
        if not self._root:
            return
        try:
            self._root.after(0, self._do_show, text)
        except Exception:
            pass

    def _do_show(self, text: str) -> None:
        # Update theme colors on each show (in case theme changed)
        bg, fg, accent = self._get_theme_colors()
        self._root.configure(bg=bg)
        self._label.config(
            text=text if text else "Listening...",
            fg=fg, bg=bg,
            font=(FONT_FAMILY, self._settings.overlay_font_size),
        )
        self._status_dot.configure(bg=bg)
        self._status_dot.itemconfig("dot", fill=accent)
        self._label.master.configure(bg=bg)

        self._root.update_idletasks()

        w = max(_MIN_WIDTH, self._label.winfo_reqwidth() + 2 * _PADDING_X + 26)
        h = self._label.winfo_reqheight() + 2 * _PADDING_Y
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x, y = self._calc_position(w, h, sw, sh)
        self._root.geometry(f"{w}x{h}+{x}+{y}")

        # Update opacity in case it changed
        self._root.attributes("-alpha", self._settings.overlay_opacity)

        if not self._visible:
            self._root.deiconify()
            self._visible = True

    def _calc_position(self, w: int, h: int, sw: int, sh: int) -> tuple[int, int]:
        """Calculate overlay x, y based on the position preference."""
        pos = self._settings.overlay_position
        margin = _MARGIN
        if pos == "top-center":
            return (sw - w) // 2, margin
        elif pos == "top-left":
            return margin, margin
        elif pos == "top-right":
            return sw - w - margin, margin
        elif pos == "bottom-left":
            return margin, sh - h - margin
        elif pos == "bottom-right":
            return sw - w - margin, sh - h - margin
        else:  # bottom-center (default)
            return (sw - w) // 2, sh - h - margin

    def update_text(self, text: str) -> None:
        if not self._root:
            return
        try:
            self._root.after(0, self._do_update, text)
        except Exception:
            pass

    def _do_update(self, text: str) -> None:
        if self._label:
            self._label.config(text=text if text else "Listening...")

    def hide(self) -> None:
        if not self._root:
            return
        try:
            self._root.after(0, self._do_hide)
        except Exception:
            pass

    def _do_hide(self) -> None:
        self._root.withdraw()
        self._visible = False

    def shutdown(self) -> None:
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass
