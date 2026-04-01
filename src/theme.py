"""Design tokens and theme system for Eqho.

Three modes: dark, light, system (auto-detects Windows theme).
Inspired by GitHub's design system (neutral, functional) with VoiceOS
influence (rounded, spacious). Accent is a soft blue, not GitHub green.
"""

from dataclasses import dataclass
from typing import Optional
import logging

log = logging.getLogger(__name__)

# -- Design tokens (constant across themes) -----------------------------------

RADIUS_SM = 6      # inputs, buttons, small chips
RADIUS_MD = 10     # cards, panels, dropdowns
RADIUS_LG = 14     # overlay bar, modal windows, dashboard frame
RADIUS_XL = 18     # pill switcher, large containers

ACCENT = "#58a6ff"          # soft blue (GitHub-adjacent, not identical)
ACCENT_HOVER = "#79b8ff"
ACCENT_MUTED = "#1f3a5f"    # dark mode accent bg
ACCENT_LIGHT_MUTED = "#dbeafe"  # light mode accent bg

SUCCESS = "#3fb950"
SUCCESS_MUTED = "#1a3a2a"
WARNING = "#d29922"
WARNING_MUTED = "#3d2e00"
DANGER = "#f85149"

FONT_FAMILY = "Inter"
FONT_SIZES = {
    "xs": 10,
    "sm": 11,
    "base": 13,
    "lg": 15,
    "xl": 18,
    "2xl": 22,
    "3xl": 28,
}

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "2xl": 32,
}


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for a single theme mode."""
    bg_primary: str       # main window background
    bg_secondary: str     # sidebar, cards
    bg_tertiary: str      # input fields, nested cards
    bg_hover: str         # hover state for interactive elements
    fg_primary: str       # main text
    fg_secondary: str     # labels, descriptions
    fg_muted: str         # placeholders, disabled text
    border: str           # borders, dividers
    border_subtle: str    # very subtle separators
    accent: str           # primary action color
    accent_hover: str
    accent_muted: str     # accent background (tags, badges)
    success: str
    success_muted: str
    warning: str
    warning_muted: str
    danger: str
    # Overlay specific
    overlay_bg: str
    overlay_fg: str
    overlay_accent: str


DARK = ThemeColors(
    bg_primary="#0d1117",
    bg_secondary="#161b22",
    bg_tertiary="#21262d",
    bg_hover="#30363d",
    fg_primary="#e6edf3",
    fg_secondary="#8b949e",
    fg_muted="#484f58",
    border="#30363d",
    border_subtle="#21262d",
    accent=ACCENT,
    accent_hover=ACCENT_HOVER,
    accent_muted=ACCENT_MUTED,
    success=SUCCESS,
    success_muted=SUCCESS_MUTED,
    warning=WARNING,
    warning_muted=WARNING_MUTED,
    danger=DANGER,
    overlay_bg="#161b22",
    overlay_fg="#e6edf3",
    overlay_accent=ACCENT,
)

LIGHT = ThemeColors(
    bg_primary="#f0f2f5",       # gray canvas (main background)
    bg_secondary="#ffffff",     # white cards, sidebar
    bg_tertiary="#e4e8ec",      # inputs, nested elements
    bg_hover="#d0d5dc",         # hover states
    fg_primary="#1f2328",       # main text (near-black)
    fg_secondary="#4d5562",     # labels, descriptions (darker than before)
    fg_muted="#6e7681",         # placeholders, disabled (darker)
    border="#c9cfd6",           # borders (more visible)
    border_subtle="#dce1e6",    # subtle separators
    accent="#0969da",
    accent_hover="#0550ae",
    accent_muted=ACCENT_LIGHT_MUTED,
    success="#1a7f37",
    success_muted="#dafbe1",
    warning="#9a6700",
    warning_muted="#fff8c5",
    danger="#cf222e",
    overlay_bg="#ffffff",
    overlay_fg="#1f2328",
    overlay_accent="#0969da",
)


def get_system_theme() -> str:
    """Detect Windows light/dark mode. Returns 'dark' or 'light'."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except Exception:
        return "dark"


def get_colors(mode: str) -> ThemeColors:
    """Get the color palette for the given mode ('dark', 'light', 'system')."""
    if mode == "system":
        mode = get_system_theme()
    return LIGHT if mode == "light" else DARK


# -- Model metadata for the UI ------------------------------------------------

MODEL_INFO = {
    "distil-large-v3": {
        "name": "Distil Large v3",
        "size": "~1.5 GB",
        "lang": "English optimized",
        "device": "GPU accelerated",
        "rec": "Recommended for most users",
        "icon": "✓",
    },
    "distil-medium.en": {
        "name": "Distil Medium EN",
        "size": "~750 MB",
        "lang": "English optimized",
        "device": "GPU accelerated",
        "rec": "Lighter, still great for English",
        "icon": "✓",
    },
    "distil-small.en": {
        "name": "Distil Small EN",
        "size": "~330 MB",
        "lang": "English optimized",
        "device": "GPU accelerated",
        "rec": "Fastest English, slightly lower accuracy",
        "icon": "✓",
    },
    "large-v3-turbo": {
        "name": "Large v3 Turbo",
        "size": "~1.6 GB",
        "lang": "100+ languages",
        "device": "GPU accelerated",
        "rec": "Best multilingual option",
        "icon": "✓",
    },
    "medium": {
        "name": "Medium",
        "size": "~1.5 GB",
        "lang": "100+ languages",
        "device": "GPU accelerated",
        "rec": "Solid multilingual fallback",
        "icon": "✓",
    },
    "small": {
        "name": "Small",
        "size": "~950 MB",
        "lang": "100+ languages",
        "device": "GPU accelerated",
        "rec": "Balanced speed and accuracy",
        "icon": "✓",
    },
    "base": {
        "name": "Base",
        "size": "~300 MB",
        "lang": "100+ languages",
        "device": "GPU accelerated",
        "rec": "Lightweight multilingual",
        "icon": "✓",
    },
    "tiny": {
        "name": "Tiny",
        "size": "~150 MB",
        "lang": "100+ languages",
        "device": "GPU accelerated",
        "rec": "Fastest, least accurate",
        "icon": "✓",
    },
    "large-v3": {
        "name": "Large v3",
        "size": "~3.1 GB",
        "lang": "100+ languages",
        "device": "CPU only (too large for 6 GB VRAM)",
        "rec": "Highest accuracy, significantly slower",
        "icon": "⚠",
    },
}
