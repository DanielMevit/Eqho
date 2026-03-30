"""Global hotkey listener supporting hold-to-talk and toggle modes."""

import logging
import threading
from typing import Callable, Optional

import keyboard

from .settings import Settings

log = logging.getLogger(__name__)


class HotkeyManager:
    """Registers a global hotkey and calls back on press/release."""

    def __init__(
        self,
        settings: Settings,
        on_activate: Callable[[], None],
        on_deactivate: Callable[[], None],
    ):
        self._settings = settings
        self._on_activate = on_activate
        self._on_deactivate = on_deactivate
        self._active = False
        self._registered = False
        self._lock = threading.Lock()

    def register(self) -> None:
        if self._registered:
            self.unregister()

        combo = self._settings.hotkey
        mode = self._settings.hotkey_mode

        if mode == "hold":
            keyboard.on_press_key(
                self._last_key(combo),
                self._on_hold_press,
                suppress=False,
            )
            keyboard.on_release_key(
                self._last_key(combo),
                self._on_hold_release,
                suppress=False,
            )
        else:
            keyboard.add_hotkey(combo, self._on_toggle, suppress=False)

        self._registered = True
        log.info("Hotkey registered: %s (%s mode)", combo, mode)

    def unregister(self) -> None:
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        self._registered = False
        self._active = False

    def _last_key(self, combo: str) -> str:
        return combo.split("+")[-1].strip()

    def _modifiers_held(self) -> bool:
        combo = self._settings.hotkey
        parts = [p.strip().lower() for p in combo.split("+")]
        mods = parts[:-1]
        for m in mods:
            if not keyboard.is_pressed(m):
                return False
        return True

    # -- Toggle mode ----------------------------------------------------------

    def _on_toggle(self) -> None:
        with self._lock:
            if self._active:
                self._active = False
                self._on_deactivate()
            else:
                self._active = True
                self._on_activate()

    # -- Hold mode ------------------------------------------------------------

    def _on_hold_press(self, _event) -> None:
        if not self._modifiers_held():
            return
        with self._lock:
            if not self._active:
                self._active = True
                self._on_activate()

    def _on_hold_release(self, _event) -> None:
        with self._lock:
            if self._active:
                self._active = False
                self._on_deactivate()

    @property
    def is_active(self) -> bool:
        return self._active
