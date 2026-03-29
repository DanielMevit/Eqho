"""System tray icon with menu for Echo."""

import logging
from typing import Callable, Optional

from PIL import Image, ImageDraw
import pystray

from .settings import Settings, SUPPORTED_LANGUAGES

log = logging.getLogger(__name__)


def _create_icon_image(active: bool = False) -> Image.Image:
    """Generate a 64x64 tray icon programmatically."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg = "#89b4fa" if active else "#45475a"
    fg = "#1e1e2e" if active else "#cdd6f4"

    draw.rounded_rectangle([2, 2, size - 2, size - 2], radius=14, fill=bg)

    # Microphone shape
    cx, cy = size // 2, size // 2 - 4
    draw.rounded_rectangle([cx - 7, cy - 14, cx + 7, cy + 6], radius=6, fill=fg)
    draw.arc([cx - 12, cy - 4, cx + 12, cy + 14], 0, 180, fill=fg, width=3)
    draw.line([cx, cy + 14, cx, cy + 20], fill=fg, width=3)
    draw.line([cx - 6, cy + 20, cx + 6, cy + 20], fill=fg, width=3)

    return img


class TrayApp:
    """System tray application controller."""

    def __init__(
        self,
        settings: Settings,
        on_toggle: Callable[[], None],
        on_quit: Callable[[], None],
        on_settings_changed: Callable[[], None],
    ):
        self._settings = settings
        self._on_toggle = on_toggle
        self._on_quit = on_quit
        self._on_settings_changed = on_settings_changed
        self._icon: Optional[pystray.Icon] = None
        self._is_active = False

    def run(self) -> None:
        """Blocking -- runs the tray icon event loop."""
        self._icon = pystray.Icon(
            "Echo",
            icon=_create_icon_image(False),
            title="Echo",
            menu=self._build_menu(),
        )
        self._icon.run()

    def set_active(self, active: bool) -> None:
        self._is_active = active
        if self._icon:
            self._icon.icon = _create_icon_image(active)
            title = "Echo - Listening..." if active else "Echo"
            self._icon.title = title

    def notify(self, message: str) -> None:
        if self._icon:
            try:
                self._icon.notify(message, "Echo")
            except Exception:
                pass

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                lambda _: "Stop Listening" if self._is_active else "Start Listening",
                self._toggle_click,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Hotkey Mode", pystray.Menu(
                pystray.MenuItem(
                    "Toggle (press once)",
                    self._set_mode_toggle,
                    checked=lambda _: self._settings.hotkey_mode == "toggle",
                    radio=True,
                ),
                pystray.MenuItem(
                    "Hold to talk",
                    self._set_mode_hold,
                    checked=lambda _: self._settings.hotkey_mode == "hold",
                    radio=True,
                ),
            )),
            pystray.MenuItem("Paste Mode", pystray.Menu(
                pystray.MenuItem(
                    "Clipboard paste (fast)",
                    self._set_paste_clipboard,
                    checked=lambda _: self._settings.auto_paste,
                    radio=True,
                ),
                pystray.MenuItem(
                    "Simulated typing",
                    self._set_paste_typing,
                    checked=lambda _: not self._settings.auto_paste,
                    radio=True,
                ),
            )),
            pystray.MenuItem("Language", self._language_submenu()),
            pystray.MenuItem("Show Overlay", self._toggle_overlay,
                             checked=lambda _: self._settings.overlay_enabled),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit_click),
        )

    def _language_submenu(self) -> pystray.Menu:
        items = []
        for code, name in SUPPORTED_LANGUAGES.items():
            items.append(pystray.MenuItem(
                f"{name} ({code})",
                self._make_lang_setter(code),
                checked=lambda _, c=code: self._settings.language == c,
                radio=True,
            ))
        return pystray.Menu(*items)

    def _make_lang_setter(self, code: str):
        def _set(icon, item):
            self._settings.language = code
            self._settings.save()
            self._on_settings_changed()
        return _set

    def _toggle_click(self, icon, item) -> None:
        self._on_toggle()

    def _quit_click(self, icon, item) -> None:
        self._on_quit()
        icon.stop()

    def _set_mode_toggle(self, icon, item) -> None:
        self._settings.hotkey_mode = "toggle"
        self._settings.save()
        self._on_settings_changed()

    def _set_mode_hold(self, icon, item) -> None:
        self._settings.hotkey_mode = "hold"
        self._settings.save()
        self._on_settings_changed()

    def _set_paste_clipboard(self, icon, item) -> None:
        self._settings.auto_paste = True
        self._settings.save()

    def _set_paste_typing(self, icon, item) -> None:
        self._settings.auto_paste = False
        self._settings.save()

    def _toggle_overlay(self, icon, item) -> None:
        self._settings.overlay_enabled = not self._settings.overlay_enabled
        self._settings.save()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
