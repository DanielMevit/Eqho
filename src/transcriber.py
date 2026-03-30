"""Faster-whisper transcriber with live mic recording and VAD-based chunking."""

import logging
import os
import queue
import threading
import time
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from .settings import Settings, MODEL_CACHE_DIR

log = logging.getLogger(__name__)

os.environ["HF_HUB_CACHE"] = str(MODEL_CACHE_DIR / "huggingface")


def _disable_windows_audio_ducking() -> None:
    """Tell Windows not to adjust other apps' volume when we use the mic.

    Sets the registry key so Windows Communications Activity is "Do nothing"
    instead of ducking/boosting other audio when a mic is in use.
    """
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Multimedia\Audio"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                            winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current, _ = winreg.QueryValueEx(key, "UserDuckingPreference")
                if current == 3:  # already set to "Do nothing"
                    return
            except FileNotFoundError:
                pass
            # 3 = "Do nothing" (0=mute, 1=reduce 80%, 2=reduce 50%)
            winreg.SetValueEx(key, "UserDuckingPreference", 0, winreg.REG_DWORD, 3)
            log.info("Disabled Windows audio ducking (Communications Activity → Do nothing).")
    except Exception as e:
        log.debug("Could not disable audio ducking: %s", e)

SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5
SILENCE_THRESHOLD = 0.003
SILENCE_TIMEOUT = 1.2
MIN_PHRASE_DURATION = 0.4
PARTIAL_INTERVAL = 1.5  # send a partial transcription every N seconds of active speech


_CPU_ONLY_MODELS = {"large-v3"}  # too large for 6GB VRAM

def _pick_device_and_compute(model_size: str) -> tuple[str, str]:
    """Choose CUDA or CPU and appropriate compute type based on model + hardware."""
    if model_size in _CPU_ONLY_MODELS:
        return "cpu", "int8"
    try:
        import ctranslate2
        cuda_types = ctranslate2.get_supported_compute_types("cuda")
        if "int8_float16" in cuda_types:
            log.info("CUDA compute types available: %s", cuda_types)
            return "cuda", "int8_float16"
    except Exception:
        pass
    return "cpu", "int8"


class VoiceTranscriber:
    """Records from mic, detects speech via energy-based VAD, transcribes with faster-whisper."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._model: Optional[WhisperModel] = None
        _disable_windows_audio_ducking()
        self._on_partial: Optional[Callable[[str], None]] = None
        self._on_complete: Optional[Callable[[str], None]] = None
        self._running = False
        self._lock = threading.Lock()
        self._model_loaded = False
        self._stream: Optional[sd.InputStream] = None
        self._audio_q: queue.Queue = queue.Queue()
        self._worker: Optional[threading.Thread] = None
        self._current_model_size: Optional[str] = None

    def set_callbacks(
        self,
        on_partial: Callable[[str], None],
        on_complete: Callable[[str], None],
    ) -> None:
        self._on_partial = on_partial
        self._on_complete = on_complete

    def _ensure_model(self) -> None:
        target = self._settings.model_size
        if self._model_loaded and self._current_model_size == target:
            return

        MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        device, compute = _pick_device_and_compute(target)
        log.info(
            "Loading faster-whisper model=%s device=%s compute=%s cache=%s",
            target, device, compute, MODEL_CACHE_DIR,
        )
        self._model = WhisperModel(
            target,
            device=device,
            compute_type=compute,
            download_root=str(MODEL_CACHE_DIR),
        )

        # Smoke-test actual inference to catch missing CUDA DLLs (e.g. cublas64_12.dll)
        if device == "cuda":
            try:
                dummy = np.zeros(SAMPLE_RATE, dtype=np.float32)
                segments, _ = self._model.transcribe(dummy, language="en", beam_size=1)
                list(segments)  # force the generator to run
                log.info("CUDA inference verified OK.")
            except Exception as e:
                log.warning("CUDA inference failed (%s), falling back to CPU.", e)
                self._model = WhisperModel(
                    target,
                    device="cpu",
                    compute_type="int8",
                    download_root=str(MODEL_CACHE_DIR),
                )
                device, compute = "cpu", "int8"

        self._current_model_size = target
        self._model_loaded = True
        log.info("Model ready: %s on %s (%s)", target, device, compute)

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._ensure_model()
            assert self._on_partial and self._on_complete, "Set callbacks before starting"
            self._running = True

            while not self._audio_q.empty():
                try:
                    self._audio_q.get_nowait()
                except queue.Empty:
                    break

            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=int(SAMPLE_RATE * CHUNK_DURATION),
                device=self._settings.audio_device,
                callback=self._audio_callback,
            )
            self._stream.start()

            self._worker = threading.Thread(target=self._transcription_loop, daemon=True)
            self._worker.start()
            log.info("Transcription started (mic recording).")

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            log.warning("Audio callback status: %s", status)
        self._audio_q.put(indata[:, 0].copy())

    def _transcription_loop(self) -> None:
        """Accumulates audio, detects speech/silence, and transcribes phrases."""
        audio_buffer = np.array([], dtype=np.float32)
        silence_start: Optional[float] = None
        is_speaking = False
        last_partial_time: float = 0
        chunk_count = 0
        peak_rms = 0.0

        while self._running:
            try:
                chunk = self._audio_q.get(timeout=0.1)
            except queue.Empty:
                continue

            audio_buffer = np.concatenate([audio_buffer, chunk])
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            chunk_count += 1
            peak_rms = max(peak_rms, rms)

            # Log mic levels periodically so we can diagnose issues
            if chunk_count % 20 == 0:
                log.info(
                    "Mic level: RMS=%.5f peak=%.5f threshold=%.4f speaking=%s buf=%.1fs",
                    rms, peak_rms, SILENCE_THRESHOLD, is_speaking,
                    len(audio_buffer) / SAMPLE_RATE,
                )
                peak_rms = 0.0

            if rms > SILENCE_THRESHOLD:
                silence_start = None
                if not is_speaking:
                    is_speaking = True
                    last_partial_time = time.monotonic()
                    log.info("Speech detected (RMS=%.5f)", rms)

                now = time.monotonic()
                buf_duration = len(audio_buffer) / SAMPLE_RATE
                if buf_duration > 1.0 and (now - last_partial_time) >= PARTIAL_INTERVAL:
                    last_partial_time = now
                    self._do_partial(audio_buffer)
            else:
                if is_speaking:
                    if silence_start is None:
                        silence_start = time.monotonic()
                    elif time.monotonic() - silence_start > SILENCE_TIMEOUT:
                        buf_duration = len(audio_buffer) / SAMPLE_RATE
                        if buf_duration >= MIN_PHRASE_DURATION:
                            log.info("Silence detected, transcribing %.1fs of audio", buf_duration)
                            self._do_complete(audio_buffer)
                        audio_buffer = np.array([], dtype=np.float32)
                        is_speaking = False
                        silence_start = None

        # Drain any remaining chunks from the queue
        while not self._audio_q.empty():
            try:
                chunk = self._audio_q.get_nowait()
                audio_buffer = np.concatenate([audio_buffer, chunk])
            except queue.Empty:
                break

        # Flush all remaining audio on stop (don't require is_speaking —
        # the user releasing the hold key IS the stop signal)
        buf_duration = len(audio_buffer) / SAMPLE_RATE
        if buf_duration >= MIN_PHRASE_DURATION:
            log.info("Flushing remaining %.1fs of audio on stop", buf_duration)
            self._do_complete(audio_buffer)

    def _do_partial(self, audio: np.ndarray) -> None:
        try:
            segments, _ = self._model.transcribe(
                audio,
                language=self._settings.language,
                beam_size=1,
            )
            text = " ".join(s.text.strip() for s in segments if s.text.strip())
            if text and self._on_partial:
                log.info("Partial: %s", text)
                self._on_partial(text)
        except Exception as e:
            log.error("Partial transcription error: %s", e)

    def _do_complete(self, audio: np.ndarray) -> None:
        try:
            segments, _ = self._model.transcribe(
                audio,
                language=self._settings.language,
                beam_size=5,
            )
            text = " ".join(s.text.strip() for s in segments if s.text.strip())
            if text and self._on_complete:
                log.info("Complete: %s", text)
                self._on_complete(text)
        except Exception as e:
            log.error("Transcription error: %s", e)

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                return
            self._running = False

        # Wait for worker to finish (it drains the queue and flushes audio)
        if self._worker:
            self._worker.join(timeout=5)
            self._worker = None

        # Close mic AFTER worker is done so no audio chunks are lost
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        log.info("Transcription stopped.")

    def is_running(self) -> bool:
        return self._running

    def reload_model(self) -> None:
        """Reload after model size or language change."""
        was_running = self._running
        if was_running:
            self.stop()
        self._model_loaded = False
        self._model = None
        if was_running:
            self.start()

    def shutdown(self) -> None:
        self.stop()
        self._model = None
        self._model_loaded = False
