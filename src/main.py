"""Ekho -- always-on dictation app entry point.

Wires together: settings, transcriber, overlay, hotkey, tray, and injector.
"""

import logging
import threading
import time

from .settings import Settings
from .transcriber import VoiceTranscriber
from .overlay import TranscriptionOverlay
from .hotkey import HotkeyManager
from .injector import type_text, get_foreground_window, set_foreground_window
from .tray import TrayApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
# Silence noisy libraries
for _quiet in ("PIL", "httpx", "httpcore", "urllib3", "huggingface_hub"):
    logging.getLogger(_quiet).setLevel(logging.WARNING)
log = logging.getLogger("ekho")


class App:
    """Top-level application controller."""

    def __init__(self) -> None:
        self.settings = Settings.load()
        self.transcriber = VoiceTranscriber(self.settings)
        self.overlay = TranscriptionOverlay(self.settings)
        self._pending_text: list[str] = []
        self._lock = threading.Lock()
        self._target_hwnd: int = 0  # window to paste into

        self.transcriber.set_callbacks(
            on_partial=self._on_partial,
            on_complete=self._on_complete,
        )

        self.hotkey = HotkeyManager(
            self.settings,
            on_activate=self.activate,
            on_deactivate=self.deactivate,
        )

        self.tray = TrayApp(
            self.settings,
            on_toggle=self.toggle,
            on_quit=self.quit,
            on_settings_changed=self._on_settings_changed,
        )

    # -- Transcription callbacks -----------------------------------------------

    def _on_partial(self, text: str) -> None:
        self.overlay.update_text(text)

    def _on_complete(self, text: str) -> None:
        with self._lock:
            self._pending_text.append(text)
        full_so_far = " ".join(self._pending_text)
        self.overlay.update_text(full_so_far)

    # -- Activation control ----------------------------------------------------

    def activate(self) -> None:
        self._target_hwnd = get_foreground_window()
        log.info("Dictation activated (target window: %s)", self._target_hwnd)
        self._pending_text.clear()
        self.overlay.show("Listening...")
        self.tray.set_active(True)
        self.transcriber.start()

    def deactivate(self) -> None:
        log.info("Dictation deactivated")
        self.transcriber.stop()
        self.tray.set_active(False)
        self.overlay.hide()

        with self._lock:
            full_text = " ".join(t.strip() for t in self._pending_text if t.strip())
            self._pending_text.clear()

        if full_text:
            time.sleep(0.4)  # wait for modifier keys to fully release
            if self._target_hwnd:
                set_foreground_window(self._target_hwnd)
                time.sleep(0.15)  # let the window come to focus
            type_text(full_text, use_clipboard=self.settings.auto_paste)
            log.info("Injected text: %s", full_text)

    def toggle(self) -> None:
        if self.transcriber.is_running():
            self.deactivate()
        else:
            self.activate()

    # -- Settings change -------------------------------------------------------

    def _on_settings_changed(self) -> None:
        log.info("Settings changed, re-registering hotkey and reloading model")
        self.hotkey.unregister()
        self.hotkey.register()
        self.transcriber.reload_model()

    # -- Lifecycle -------------------------------------------------------------

    def run(self) -> None:
        log.info("Ekho starting...")
        log.info(
            "Model: %s | Hotkey: %s (%s mode)",
            self.settings.model_size,
            self.settings.hotkey,
            self.settings.hotkey_mode,
        )

        self.overlay.start()
        self.hotkey.register()

        threading.Thread(target=self._preload_model, daemon=True).start()

        self.tray.run()

    def _preload_model(self) -> None:
        try:
            log.info("Pre-loading model (this may download ~1.5 GB on first run)...")
            self.transcriber._ensure_model()
            log.info("Model pre-loaded and ready.")
        except Exception as e:
            log.error("Failed to pre-load model: %s", e)

    def quit(self) -> None:
        log.info("Shutting down...")
        self.hotkey.unregister()
        self.transcriber.shutdown()
        self.overlay.shutdown()
        self.settings.save()


def main() -> None:
    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()


if __name__ == "__main__":
    main()
