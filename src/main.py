"""Eqho -- always-on dictation app entry point.

Wires together: settings, transcriber, overlay, hotkey, tray, and injector.
"""

import logging
import threading
import time
from typing import Optional

from .settings import Settings, VOLUME_DUCK_OPTIONS
from .transcriber import VoiceTranscriber
from .overlay import TranscriptionOverlay
from .hotkey import HotkeyManager
from .injector import type_text, get_foreground_window, set_foreground_window

# Silent volume control via Windows Core Audio API (pycaw)
try:
    from pycaw.pycaw import AudioUtilities
    from comtypes import GUID, CoInitialize
    _GUID_NULL = GUID()
    _HAS_VOLUME_CTL = True
except Exception:
    _HAS_VOLUME_CTL = False


def _get_volume_ctl():
    """Get a fresh volume endpoint (must be called per-thread due to COM)."""
    try:
        CoInitialize()
        return AudioUtilities.GetSpeakers().EndpointVolume
    except Exception:
        return None
from .tray import TrayApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
# Silence noisy libraries
for _quiet in ("PIL", "httpx", "httpcore", "urllib3", "huggingface_hub"):
    logging.getLogger(_quiet).setLevel(logging.WARNING)
log = logging.getLogger("eqho")


class App:
    """Top-level application controller."""

    def __init__(self) -> None:
        self.settings = Settings.load()
        self.transcriber = VoiceTranscriber(self.settings)
        self.overlay = TranscriptionOverlay(self.settings)
        self._pending_text: list[str] = []
        self._lock = threading.Lock()
        self._target_hwnd: int = 0  # window to paste into
        self._saved_volume: Optional[float] = None  # for volume ducking

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

    def _duck_volume(self) -> None:
        """Silently lower system volume based on user setting."""
        if not _HAS_VOLUME_CTL:
            return
        multiplier = VOLUME_DUCK_OPTIONS.get(self.settings.volume_duck)
        if multiplier is None:  # "off"
            return
        try:
            ctl = _get_volume_ctl()
            if not ctl:
                return
            self._saved_volume = ctl.GetMasterVolumeLevelScalar()
            if multiplier == 0.0:
                ctl.SetMute(True, _GUID_NULL)
            else:
                ctl.SetMasterVolumeLevelScalar(self._saved_volume * multiplier, _GUID_NULL)
            log.info("Volume ducked: %.0f%% → %s", self._saved_volume * 100,
                     "muted" if multiplier == 0.0 else f"{self._saved_volume * multiplier * 100:.0f}%")
        except Exception as e:
            log.debug("Volume duck failed: %s", e)

    def _restore_volume(self) -> None:
        """Silently restore system volume to previous level."""
        if not _HAS_VOLUME_CTL or self._saved_volume is None:
            return
        try:
            ctl = _get_volume_ctl()
            if not ctl:
                return
            ctl.SetMute(False, _GUID_NULL)
            ctl.SetMasterVolumeLevelScalar(self._saved_volume, _GUID_NULL)
            log.info("Volume restored to %.0f%%.", self._saved_volume * 100)
            self._saved_volume = None
        except Exception as e:
            log.debug("Volume restore failed: %s", e)

    def activate(self) -> None:
        self._target_hwnd = get_foreground_window()
        log.info("Dictation activated (target window: %s)", self._target_hwnd)
        self._duck_volume()
        self._pending_text.clear()
        self.overlay.show("Listening...")
        self.tray.set_active(True)
        self.transcriber.start()

    def deactivate(self) -> None:
        log.info("Dictation deactivated")
        self.transcriber.stop()
        self._restore_volume()
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

    def _on_settings_changed(self, reload_model: bool = False) -> None:
        log.info("Settings changed, re-registering hotkey%s", " and reloading model" if reload_model else "")
        self.hotkey.unregister()
        self.hotkey.register()
        if reload_model:
            self.transcriber.reload_model()

    # -- Lifecycle -------------------------------------------------------------

    def run(self) -> None:
        log.info("Eqho starting...")
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
        self._restore_volume()  # always unmute on exit
        self.hotkey.unregister()
        self.transcriber.shutdown()
        self.overlay.shutdown()
        self.settings.save()


def _emergency_unmute() -> None:
    """Last resort: unmute system audio on any exit."""
    try:
        if _HAS_VOLUME_CTL:
            ctl = _get_volume_ctl()
            if ctl:
                ctl.SetMute(False, _GUID_NULL)
    except Exception:
        pass


def main() -> None:
    import atexit
    atexit.register(_emergency_unmute)

    app = App()
    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
    finally:
        _emergency_unmute()


if __name__ == "__main__":
    main()
