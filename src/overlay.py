"""Floating transparent overlay showing real-time partial transcription."""

import logging
import threading
import tkinter as tk
from typing import Optional

from .fonts import FONT_FAMILY
from .settings import Settings

log = logging.getLogger(__name__)

_PADDING_X = 18
_PADDING_Y = 10
_CORNER_RADIUS = 12
_BG_COLOR = "#1e1e2e"
_FG_COLOR = "#cdd6f4"
_ACCENT_COLOR = "#89b4fa"
_MARGIN_BOTTOM = 60
_MIN_WIDTH = 300


class TranscriptionOverlay:
    """A small floating bar at the bottom of the screen showing live text."""

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

    def _run_tk(self) -> None:
        self._root = tk.Tk()
        self._root.title("Eqho")
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-alpha", self._settings.overlay_opacity)
        self._root.configure(bg=_BG_COLOR)

        try:
            self._root.attributes("-transparentcolor", "")
        except tk.TclError:
            pass

        frame = tk.Frame(self._root, bg=_BG_COLOR, padx=_PADDING_X, pady=_PADDING_Y)
        frame.pack(fill=tk.BOTH, expand=True)

        self._status_dot = tk.Canvas(
            frame, width=10, height=10, bg=_BG_COLOR, highlightthickness=0
        )
        self._status_dot.create_oval(1, 1, 9, 9, fill=_ACCENT_COLOR, outline="")
        self._status_dot.pack(side=tk.LEFT, padx=(0, 8))

        self._label = tk.Label(
            frame,
            text="Listening...",
            font=(FONT_FAMILY, self._settings.overlay_font_size),
            fg=_FG_COLOR,
            bg=_BG_COLOR,
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
        self._label.config(text=text if text else "Listening...")
        self._root.update_idletasks()

        w = max(_MIN_WIDTH, self._label.winfo_reqwidth() + 2 * _PADDING_X + 26)
        h = self._label.winfo_reqheight() + 2 * _PADDING_Y
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x, y = self._calc_position(w, h, sw, sh)
        self._root.geometry(f"{w}x{h}+{x}+{y}")

        if not self._visible:
            self._root.deiconify()
            self._visible = True

    def _calc_position(self, w: int, h: int, sw: int, sh: int) -> tuple[int, int]:
        """Calculate overlay x, y based on the position preference."""
        pos = self._settings.overlay_position
        margin = _MARGIN_BOTTOM
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
