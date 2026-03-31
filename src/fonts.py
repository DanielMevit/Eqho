"""Load bundled Inter font into the Windows font table at runtime.

Uses AddFontResourceEx so the font is available to tkinter without
requiring a system-wide install. Fonts are removed on shutdown.
"""

import ctypes
import logging
from pathlib import Path

log = logging.getLogger(__name__)

_FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
_FR_PRIVATE = 0x10  # font is available only to this process
_loaded: list[str] = []


def load_fonts() -> bool:
    """Register all .otf/.ttf files in assets/fonts. Returns True if Inter is available."""
    if not _FONTS_DIR.exists():
        log.warning("Fonts directory not found: %s", _FONTS_DIR)
        return False

    try:
        gdi32 = ctypes.windll.gdi32
    except AttributeError:
        log.debug("Not on Windows, skipping font loading.")
        return False

    count = 0
    for font_file in sorted(_FONTS_DIR.glob("*.otf")) + sorted(_FONTS_DIR.glob("*.ttf")):
        path_str = str(font_file)
        result = gdi32.AddFontResourceExW(path_str, _FR_PRIVATE, 0)
        if result > 0:
            _loaded.append(path_str)
            count += 1
        else:
            log.warning("Failed to load font: %s", font_file.name)

    if count:
        log.info("Loaded %d Inter font file(s) from assets/fonts.", count)
    return count > 0


def unload_fonts() -> None:
    """Remove all fonts registered by load_fonts."""
    try:
        gdi32 = ctypes.windll.gdi32
    except AttributeError:
        return

    for path_str in _loaded:
        gdi32.RemoveFontResourceExW(path_str, _FR_PRIVATE, 0)
    _loaded.clear()


# Font family name to use in tkinter
FONT_FAMILY = "Inter"
FONT_FALLBACK = "Segoe UI"
