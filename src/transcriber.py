"""Moonshine Voice wrapper with streaming transcription and VAD."""

import logging
import threading
from typing import Callable, Optional

from moonshine_voice import (
    MicTranscriber,
    TranscriptEventListener,
    get_model_for_language,
)

from .settings import Settings

log = logging.getLogger(__name__)


class _DictationListener(TranscriptEventListener):
    """Bridges Moonshine events to our callback interface."""

    def __init__(
        self,
        on_partial: Callable[[str], None],
        on_complete: Callable[[str], None],
    ):
        self._on_partial = on_partial
        self._on_complete = on_complete
        self._current_text = ""

    def on_line_started(self, event):
        self._current_text = event.line.text
        self._on_partial(self._current_text)

    def on_line_text_changed(self, event):
        self._current_text = event.line.text
        self._on_partial(self._current_text)

    def on_line_completed(self, event):
        self._current_text = ""
        self._on_complete(event.line.text)


class VoiceTranscriber:
    """High-level wrapper around MicTranscriber with start/stop control."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._mic: Optional[MicTranscriber] = None
        self._listener: Optional[_DictationListener] = None
        self._on_partial: Optional[Callable[[str], None]] = None
        self._on_complete: Optional[Callable[[str], None]] = None
        self._running = False
        self._lock = threading.Lock()
        self._model_loaded = False

    def set_callbacks(
        self,
        on_partial: Callable[[str], None],
        on_complete: Callable[[str], None],
    ) -> None:
        self._on_partial = on_partial
        self._on_complete = on_complete

    def _ensure_model(self) -> None:
        if self._model_loaded:
            return
        lang = self._settings.language
        log.info("Loading Moonshine model for language=%s ...", lang)
        model_path, model_arch = get_model_for_language(lang)
        self._mic = MicTranscriber(
            model_path=model_path,
            model_arch=model_arch,
        )
        self._model_loaded = True
        log.info("Moonshine model loaded.")

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._ensure_model()
            assert self._on_partial and self._on_complete, "Set callbacks before starting"
            self._listener = _DictationListener(self._on_partial, self._on_complete)
            self._mic.add_listener(self._listener)
            self._mic.start()
            self._running = True
            log.info("Transcription started.")

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._mic.stop()
            if self._listener:
                self._mic.remove_listener(self._listener)
                self._listener = None
            self._running = False
            log.info("Transcription stopped.")

    def is_running(self) -> bool:
        return self._running

    def reload_model(self) -> None:
        """Reload after language change."""
        was_running = self._running
        if was_running:
            self.stop()
        self._model_loaded = False
        self._mic = None
        if was_running:
            self.start()

    def shutdown(self) -> None:
        self.stop()
        if self._mic:
            try:
                self._mic.close()
            except Exception:
                pass
            self._mic = None
            self._model_loaded = False
