"""User preferences persisted to a JSON config file."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / "Ekho"
CONFIG_FILE = CONFIG_DIR / "settings.json"

MODEL_CACHE_DIR = Path("D:/EkhoModels")

WHISPER_MODELS = {
    "distil-large-v3": "Distil Large v3 (~1.5 GB, English-optimized, recommended)",
    "distil-medium.en": "Distil Medium EN (~750 MB, fast English)",
    "distil-small.en": "Distil Small EN (~330 MB, fastest English)",
    "large-v3-turbo": "Large v3 Turbo (~1.6 GB, multilingual, near-large accuracy)",
    "medium": "Medium (~1.5 GB, multilingual)",
    "small": "Small (~950 MB, multilingual)",
    "base": "Base (~300 MB, multilingual)",
    "tiny": "Tiny (~150 MB, fastest, least accurate)",
    "large-v3": "Large v3 (~3.1 GB, highest accuracy)",
}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "zh": "Mandarin",
    "ja": "Japanese",
    "ko": "Korean",
    "vi": "Vietnamese",
    "ar": "Arabic",
    "uk": "Ukrainian",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ru": "Russian",
    "it": "Italian",
}

HOTKEY_MODES = ("toggle", "hold")


@dataclass
class Settings:
    language: str = "en"
    hotkey: str = "ctrl+alt+d"
    hotkey_mode: str = "toggle"  # "toggle" or "hold"
    model_size: str = "distil-large-v3"
    audio_device: Optional[int] = None  # None = system default
    auto_paste: bool = True  # paste via clipboard vs simulated keystrokes
    overlay_enabled: bool = True
    overlay_opacity: float = 0.85
    overlay_font_size: int = 14
    start_with_windows: bool = False

    # runtime-only (not persisted)
    _listeners: list = field(default_factory=list, repr=False)

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        data.pop("_listeners", None)
        CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> "Settings":
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                data.pop("_listeners", None)
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()

    def add_listener(self, callback) -> None:
        self._listeners.append(callback)

    def notify(self) -> None:
        for cb in self._listeners:
            cb(self)
