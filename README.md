<picture>
  <source media="(prefers-color-scheme: dark)" srcset="logo/logo_horizontal_light.png">
  <source media="(prefers-color-scheme: light)" srcset="logo/logo_horizontal_dark.png">
  <img alt="Eqho" src="logo/logo_horizontal_dark.png" width="140">
</picture>

**Your voice, everywhere.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

An always-on dictation app that runs in your system tray. Press a hotkey, speak, and your words are typed into whatever application is focused. Powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) -- a fast, accurate, on-device speech-to-text engine built on OpenAI's Whisper model via CTranslate2.

## Features

- **Real-time transcription** -- see words appear as you speak via a floating overlay
- **100% local** -- no cloud, no API keys, everything runs on your machine
- **System tray** -- runs silently in the background
- **Global hotkey** -- works in any application (default: `Alt+Q`)
- **Toggle or hold-to-talk** modes
- **Auto-paste** into the active window via clipboard or simulated keystrokes
- **Multi-language** -- English, Spanish, Mandarin, Japanese, Korean, Vietnamese, Arabic, Ukrainian, French, German, Portuguese, Russian, Italian
- **Model selection** -- Distil-Whisper (English-optimized), Large v3 Turbo, Medium, Small, Base, Tiny, Large v3
- **GPU acceleration** -- uses CUDA when available (NVIDIA GPUs), falls back to CPU gracefully
- **English-optimized default** -- ships with Distil-Large-v3 (6x faster than Large v3, <1% accuracy loss)
- **Settings dashboard** -- modern customtkinter window with sidebar navigation, theme switching, model cards, responsive layout
- **Theme system** -- dark, light, and system (auto-detect) modes

## Supported Languages

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | `en` | Arabic | `ar` |
| Spanish | `es` | Ukrainian | `uk` |
| Mandarin | `zh` | French | `fr` |
| Japanese | `ja` | German | `de` |
| Korean | `ko` | Portuguese | `pt` |
| Vietnamese | `vi` | Russian | `ru` |
| Italian | `it` | | |

Distil models (`distil-large-v3`, `distil-medium.en`, `distil-small.en`) are optimized for English. For other languages, use a multilingual model like `large-v3-turbo` or `medium`.

## Prerequisites

- **Python 3.10+**
- **NVIDIA GPU (recommended):** Install [CUDA Toolkit 12.x](https://developer.nvidia.com/cuda-downloads) for GPU-accelerated transcription. Without it, the app falls back to CPU (slower but functional).
  - Quick install via winget: `winget install Nvidia.CUDA --version 12.9`
  - After installing, **restart your terminal** so the new PATH is picked up.

## Quick Start

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python run.py
```

The app will:
1. Appear as an icon in your system tray (bottom-right, may be behind the `^` arrow)
2. Pre-load the Distil-Large-v3 model in the background (~1.5 GB, cached in `D:\EqhoModels` after first download)
3. Wait for you to press **Alt+Q**

### How to dictate

1. Click into the app where you want text (Word, browser, Notepad, etc.)
2. Press **Alt+Q** -- a floating bar appears saying "Listening..."
3. Speak naturally, pause ~1-2 seconds between phrases
4. The overlay updates with your transcribed words
5. Press **Alt+Q** again to stop -- text is pasted into the focused app

## Note on Transcription Accuracy

Eqho uses OpenAI's Whisper models for speech recognition. Whisper is known to occasionally hallucinate — producing words, phrases, or repeated text that were not actually spoken. This is a [documented limitation](https://github.com/openai/whisper/discussions/928) of the Whisper model family, not specific to Eqho. It tends to happen more with background noise, silence, or non-English languages. Smaller models are more prone to this than larger ones.

In my case, the model can sometimes be a bit too polite — it keeps printing "thank you, thank you" out of nowhere. I'm somewhere between grateful and terrified.

## System Tray Menu

Right-click the tray icon for:
- **Start/Stop Listening** -- toggle dictation (same as hotkey)
- **Microphone** -- pick which mic to use
- **Model** -- switch between Distil (English), Turbo, Medium, Small, Base, Tiny, Large v3
- **Dashboard...** -- open the full settings dashboard
- **Hotkey Mode** -- switch between toggle and hold-to-talk
- **Paste Mode** -- clipboard paste (fast) or simulated typing
- **Language** -- switch transcription language
- **Volume While Speaking** -- mute or reduce system volume during dictation
- **Show Overlay** -- toggle the floating preview bar
- **Overlay Position** -- choose where the overlay appears (bottom-center, top-center, corners)
- **Start with Windows** -- auto-launch Eqho on login
- **Quit** -- exit the app

## Configuration

Settings are saved to `%APPDATA%\Eqho\settings.json` and persist across sessions.

| Setting | Default | Description |
|---------|---------|-------------|
| `hotkey` | `alt+q` | Global hotkey combo |
| `hotkey_mode` | `toggle` | `toggle` or `hold` |
| `model_size` | `distil-large-v3` | Whisper model (see Model menu for full list) |
| `language` | `en` | Two-letter language code |
| `auto_paste` | `true` | Use clipboard paste vs simulated typing |
| `overlay_enabled` | `true` | Show floating transcription bar |
| `overlay_opacity` | `0.85` | Overlay window opacity |
| `overlay_font_size` | `14` | Overlay text size |
| `overlay_position` | `bottom-center` | Overlay screen position |
| `volume_duck` | `mute` | Volume during dictation: off, 50%, 25%, 10%, mute |
| `start_with_windows` | `false` | Auto-start on Windows login |
| `theme` | `dark` | Color theme: dark, light, system |

## Models

| Model | Size | Language | Speed (GPU) | Speed (CPU) | Notes |
|-------|------|----------|-------------|-------------|-------|
| **distil-large-v3** | ~1.5 GB | English | ~0.3s | ~1-2s | Default. Best English accuracy/speed ratio |
| distil-medium.en | ~750 MB | English | ~0.2s | ~1s | Lighter, still great for English |
| distil-small.en | ~330 MB | English | ~0.1s | <1s | Fastest English, slightly lower accuracy |
| large-v3-turbo | ~1.6 GB | 100+ langs | ~0.5s | ~2-3s | Best multilingual option |
| medium | ~1.5 GB | 100+ langs | ~0.5s | ~2-4s | Solid multilingual fallback |
| large-v3 | ~3.1 GB | 100+ langs | CPU-only* | ~4-6s | Highest accuracy, too large for 6GB VRAM |

*GPU speeds measured on RTX 3060 Laptop (6GB VRAM). CUDA Toolkit 12.x required.*

The app auto-detects CUDA. If `cublas64_12.dll` is not found, it logs a warning and falls back to CPU automatically.

## Structure

```
Eqho/
  README.md            -- this file
  CHANGELOG.md         -- timestamped release notes
  ROADMAP.md           -- planned features & milestones
  COMMANDS.md          -- PowerShell command reference
  LICENSE              -- AGPL-3.0 license
  requirements.txt     -- Python dependencies
  run.py               -- top-level launcher
  Eqho.spec            -- PyInstaller config
  build.ps1            -- build script for standalone .exe
  agent-instructions/  -- internal agent guidance (SOUL, AGENTS, TODO)
  src/
    __init__.py
    __main__.py         -- python -m src support
    main.py             -- entry point, wires all modules
    settings.py         -- config persistence (%AppData%\Eqho)
    transcriber.py      -- faster-whisper wrapper with energy-based VAD
    audio.py            -- microphone device enumeration
    overlay.py          -- floating transcription preview (tkinter)
    hotkey.py           -- global hotkey listener
    injector.py         -- text injection into active app (with window focus restore)
    tray.py             -- system tray icon & menu
    settings_ui.py      -- legacy hotkey capture window
    dashboard.py        -- settings dashboard (customtkinter)
    theme.py            -- design tokens, color palettes, theme system
    fonts.py            -- Inter font loader (Windows AddFontResourceEx)
  assets/
    icon_64.png         -- legacy tray icon (full brightness)
    icon_64_active.png  -- legacy tray icon (active/listening)
    icon_64_inactive.png -- legacy tray icon (dimmed/idle)
    logo_62_dark.png    -- tray icon (62px "e" mark, blue on transparent)
    logo_62_white.png   -- tray icon (62px "e" mark, white on transparent)
    logo_32_dark.png    -- small logo (32px "e" mark, blue)
    logo_32_white.png   -- small logo (32px "e" mark, white)
    logo_horizontal_dark.png  -- wordmark (140x60, dark text for light theme)
    logo_horizontal_light.png -- wordmark (140x60, light text for dark theme)
    eqho.ico            -- Windows .ico for packaged .exe
    fonts/
      Inter-*.otf       -- Inter font family (Regular, Medium, SemiBold, Bold)
      LICENSE-Inter.txt  -- SIL Open Font License
  logo/
    eqho_logo.svg       -- project logo (vector source)
    eqho_logo.ai        -- project logo (Illustrator source)
    logo_horizontal_dark.png  -- wordmark for light backgrounds
    logo_horizontal_light.png -- wordmark for dark backgrounds
    logo_32_dark.png    -- 32px mark (blue)
    logo_32_white.png   -- 32px mark (white)
    logo_62_dark.png    -- 62px mark (blue)
    logo_62_white.png   -- 62px mark (white)
```

## Building a Standalone .exe

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

The executable will be at `dist\Eqho.exe`. To start automatically with Windows, copy it to your Startup folder:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## Tech

- Python 3.10+
- faster-whisper (Whisper via CTranslate2, MIT license, on-device)
- CUDA Toolkit 12.x (optional, for GPU acceleration on NVIDIA GPUs)
- pystray + Pillow (system tray)
- keyboard (global hotkeys)
- pynput + pyperclip (text injection)
- tkinter (overlay)
- customtkinter (dashboard UI)
- sounddevice + numpy (audio capture and processing)
- Target: Windows 10/11

## Changelog

For timestamped release notes, see `CHANGELOG.md`.

## Disclaimer

This software is provided "as is", without warranty of any kind. Use at your own risk. The author is not responsible for any damages, data loss, or other issues arising from the use of this software.

## License

Eqho is licensed under the [GNU Affero General Public License v3.0](LICENSE).
