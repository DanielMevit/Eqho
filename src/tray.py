"""System tray icon with menu for Ekho."""

import logging
import sys
from pathlib import Path
from typing import Callable, Optional

from PIL import Image, ImageDraw
import pystray

from .settings import Settings, SUPPORTED_LANGUAGES, WHISPER_MODELS

log = logging.getLogger(__name__)

_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def _load_icon(active: bool = False) -> Image.Image:
    """Load pre-rendered icon PNGs, fall back to programmatic generation."""
    if active:
        path = _ASSETS / "icon_64_active.png"
    else:
        path = _ASSETS / "icon_64_inactive.png"
    if path.exists():
        return Image.open(path).convert("RGBA")
    path_default = _ASSETS / "icon_64.png"
    if path_default.exists():
        return Image.open(path_default).convert("RGBA")
    return _create_icon_fallback(active)


def _create_icon_fallback(active: bool = False) -> Image.Image:
    """Programmatic fallback using Ekho's gradient palette."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=10, fill="#000000")

    bars = [0.3, 0.5, 0.8, 1.0, 0.7, 0.9, 0.6, 0.4, 0.7, 1.0, 0.8, 0.5, 0.3]
    bar_w, gap = 3, 1
    total_w = len(bars) * (bar_w + gap) - gap
    start_x = (size - total_w) // 2
    cx, cy = size // 2, size // 2
    max_h = size * 0.6

    for i, h_frac in enumerate(bars):
        x = start_x + i * (bar_w + gap)
        h = int(max_h * h_frac)
        t = i / (len(bars) - 1)
        if active:
            r, g, b = int(0), int(255 * (1 - t) + 191 * t), int(171 * (1 - t) + 255 * t)
        else:
            r, g, b = 0, int((255 * (1 - t) + 191 * t) / 3), int((171 * (1 - t) + 255 * t) / 3)
        draw.rounded_rectangle(
            [x, cy - h // 2, x + bar_w, cy + h // 2],
            radius=bar_w // 2,
            fill=(r, g, b),
        )
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
        self._icon = pystray.Icon(
            "Ekho",
            icon=_load_icon(False),
            title="Ekho",
            menu=self._build_menu(),
        )
        self._icon.run()

    def set_active(self, active: bool) -> None:
        self._is_active = active
        if self._icon:
            self._icon.icon = _load_icon(active)
            title = "Ekho - Listening..." if active else "Ekho"
            self._icon.title = title

    def notify(self, message: str) -> None:
        if self._icon:
            try:
                self._icon.notify(message, "Ekho")
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
            pystray.MenuItem("Model", self._model_submenu()),
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

    def _model_submenu(self) -> pystray.Menu:
        items = []
        for key, label in WHISPER_MODELS.items():
            items.append(pystray.MenuItem(
                label,
                self._make_model_setter(key),
                checked=lambda _, k=key: self._settings.model_size == k,
                radio=True,
            ))
        return pystray.Menu(*items)

    def _make_model_setter(self, key: str):
        def _set(icon, item):
            if self._settings.model_size != key:
                self._settings.model_size = key
                self._settings.save()
                self._on_settings_changed()
        return _set

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
