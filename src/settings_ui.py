"""Dark-themed settings window with press-to-capture hotkey binding.

Uses tkinter since it's already a dependency (overlay uses it).
"""

import logging
import threading
import tkinter as tk
from typing import Callable, Optional

import keyboard

from .fonts import FONT_FAMILY
from .settings import Settings

log = logging.getLogger(__name__)

# Eqho dark palette
_BG = "#0f0f1a"
_BG_CARD = "#1a1a2e"
_BG_INPUT = "#252540"
_FG = "#e2e2f0"
_FG_DIM = "#8888a0"
_ACCENT = "#00d4aa"
_ACCENT_HOVER = "#00f0c0"
_DANGER = "#ff4466"
_BORDER = "#2a2a45"
_FONT = (FONT_FAMILY, 11)
_FONT_TITLE = (FONT_FAMILY, 14, "bold")
_FONT_LABEL = (FONT_FAMILY, 10)
_FONT_HOTKEY = (FONT_FAMILY, 16, "bold")


class SettingsWindow:
    """A modal-ish dark settings window for hotkey configuration."""

    def __init__(self, settings: Settings, on_hotkey_changed: Callable[[], None]):
        self._settings = settings
        self._on_hotkey_changed = on_hotkey_changed
        self._win: Optional[tk.Toplevel] = None
        self._capturing = False
        self._captured_keys: set[str] = set()
        self._capture_hook = None
        self._hotkey_label: Optional[tk.Label] = None
        self._capture_btn: Optional[tk.Label] = None
        self._current_combo = self._settings.hotkey

    def show(self, parent_root: Optional[tk.Tk] = None) -> None:
        """Open the settings window. Can be called from any thread."""
        if self._win is not None:
            try:
                self._win.lift()
                self._win.focus_force()
                return
            except tk.TclError:
                self._win = None

        if parent_root:
            parent_root.after(0, lambda: self._create_window(parent_root))
        else:
            t = threading.Thread(target=self._run_standalone, daemon=True)
            t.start()

    def _run_standalone(self) -> None:
        root = tk.Tk()
        root.withdraw()
        self._create_window(root)
        root.mainloop()

    def _create_window(self, parent: tk.Tk) -> None:
        self._win = tk.Toplevel(parent)
        self._win.title("Eqho Settings")
        self._win.configure(bg=_BG)
        self._win.resizable(False, False)
        self._win.attributes("-topmost", True)

        # Window size and centering
        w, h = 380, 260
        sw = self._win.winfo_screenwidth()
        sh = self._win.winfo_screenheight()
        self._win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        # Prevent background interaction
        self._win.grab_set()
        self._win.protocol("WM_DELETE_WINDOW", self._close)

        self._build_ui()

    def _build_ui(self) -> None:
        win = self._win

        # Title
        tk.Label(
            win, text="Settings", font=_FONT_TITLE,
            fg=_FG, bg=_BG, anchor="w",
        ).pack(fill=tk.X, padx=24, pady=(20, 16))

        # Hotkey section card
        card = tk.Frame(win, bg=_BG_CARD, highlightbackground=_BORDER, highlightthickness=1)
        card.pack(fill=tk.X, padx=24, pady=(0, 12))

        tk.Label(
            card, text="Global Hotkey", font=_FONT_LABEL,
            fg=_FG_DIM, bg=_BG_CARD, anchor="w",
        ).pack(fill=tk.X, padx=16, pady=(12, 4))

        # Hotkey display
        hotkey_frame = tk.Frame(card, bg=_BG_INPUT, highlightbackground=_BORDER, highlightthickness=1)
        hotkey_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        self._hotkey_label = tk.Label(
            hotkey_frame,
            text=self._format_hotkey(self._current_combo),
            font=_FONT_HOTKEY,
            fg=_ACCENT, bg=_BG_INPUT,
            anchor="center",
            pady=10,
        )
        self._hotkey_label.pack(fill=tk.X)

        # Capture button
        self._capture_btn = tk.Label(
            hotkey_frame,
            text="Click to change",
            font=_FONT_LABEL,
            fg=_FG_DIM, bg=_BG_INPUT,
            cursor="hand2",
            pady=4,
        )
        self._capture_btn.pack(fill=tk.X)
        self._capture_btn.bind("<Button-1>", self._start_capture)

        # Buttons row
        btn_frame = tk.Frame(win, bg=_BG)
        btn_frame.pack(fill=tk.X, padx=24, pady=(8, 20))

        cancel_btn = tk.Label(
            btn_frame, text="Cancel", font=_FONT,
            fg=_FG_DIM, bg=_BG, cursor="hand2",
            padx=16, pady=6,
        )
        cancel_btn.pack(side=tk.LEFT)
        cancel_btn.bind("<Button-1>", lambda e: self._close())

        save_btn = tk.Label(
            btn_frame, text="  Save  ", font=_FONT,
            fg=_BG, bg=_ACCENT, cursor="hand2",
            padx=16, pady=6,
        )
        save_btn.pack(side=tk.RIGHT)
        save_btn.bind("<Button-1>", lambda e: self._save())
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=_ACCENT_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=_ACCENT))

    def _format_hotkey(self, combo: str) -> str:
        return " + ".join(part.strip().title() for part in combo.split("+"))

    def _start_capture(self, event=None) -> None:
        if self._capturing:
            return
        self._capturing = True
        self._captured_keys.clear()
        self._hotkey_label.config(text="Press a key combo...", fg=_DANGER)
        self._capture_btn.config(text="Press Esc to cancel")

        # Hook all keyboard events to capture the combo
        self._capture_hook = keyboard.hook(self._on_capture_event, suppress=False)

    def _on_capture_event(self, event) -> None:
        if not self._capturing:
            return

        name = event.name.lower() if event.name else ""

        # Esc cancels capture
        if name == "esc":
            self._stop_capture(cancelled=True)
            return

        if event.event_type == keyboard.KEY_DOWN:
            self._captured_keys.add(name)
            # Show current combo in real-time
            combo = self._keys_to_combo(self._captured_keys)
            try:
                self._hotkey_label.after(0, lambda: self._hotkey_label.config(
                    text=self._format_hotkey(combo), fg=_ACCENT))
            except Exception:
                pass

        elif event.event_type == keyboard.KEY_UP:
            # On key release, if we have at least one key, finalize
            if len(self._captured_keys) >= 1:
                combo = self._keys_to_combo(self._captured_keys)
                self._current_combo = combo
                self._stop_capture(cancelled=False)

    def _keys_to_combo(self, keys: set[str]) -> str:
        """Convert a set of key names to a hotkey combo string."""
        modifiers = []
        regular = []
        mod_names = {"ctrl", "left ctrl", "right ctrl", "alt", "left alt", "right alt",
                     "shift", "left shift", "right shift", "left windows", "right windows"}
        mod_map = {
            "left ctrl": "ctrl", "right ctrl": "ctrl",
            "left alt": "alt", "right alt": "alt",
            "left shift": "shift", "right shift": "shift",
            "left windows": "win", "right windows": "win",
        }
        for k in keys:
            if k in mod_names:
                canonical = mod_map.get(k, k)
                if canonical not in modifiers:
                    modifiers.append(canonical)
            else:
                regular.append(k)
        # Sort modifiers in conventional order
        mod_order = {"ctrl": 0, "alt": 1, "shift": 2, "win": 3}
        modifiers.sort(key=lambda m: mod_order.get(m, 9))
        return "+".join(modifiers + regular)

    def _stop_capture(self, cancelled: bool) -> None:
        self._capturing = False
        if self._capture_hook is not None:
            try:
                keyboard.unhook(self._capture_hook)
            except Exception:
                pass
            self._capture_hook = None

        if cancelled:
            self._current_combo = self._settings.hotkey
            try:
                self._hotkey_label.after(0, lambda: self._hotkey_label.config(
                    text=self._format_hotkey(self._current_combo), fg=_ACCENT))
                self._capture_btn.after(0, lambda: self._capture_btn.config(text="Click to change"))
            except Exception:
                pass
        else:
            try:
                self._capture_btn.after(0, lambda: self._capture_btn.config(text="Click to change"))
            except Exception:
                pass

    def _save(self) -> None:
        if self._capturing:
            self._stop_capture(cancelled=True)
        if self._current_combo and self._current_combo != self._settings.hotkey:
            self._settings.hotkey = self._current_combo
            self._settings.save()
            log.info("Hotkey changed to: %s", self._current_combo)
            self._on_hotkey_changed()
        self._close()

    def _close(self) -> None:
        if self._capturing:
            self._stop_capture(cancelled=True)
        if self._win:
            try:
                self._win.grab_release()
                self._win.destroy()
            except Exception:
                pass
            self._win = None
