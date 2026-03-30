# Ekho

**Your voice, everywhere.**

An always-on dictation app that runs in your system tray. Press a hotkey, speak, and your words are typed into whatever application is focused. Powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper) -- a fast, accurate, on-device speech-to-text engine built on OpenAI's Whisper model via CTranslate2.

## Features

- **Real-time transcription** -- see words appear as you speak via a floating overlay
- **100% local** -- no cloud, no API keys, everything runs on your machine
- **System tray** -- runs silently in the background
- **Global hotkey** -- works in any application (default: `Ctrl+Shift+Space`)
- **Toggle or hold-to-talk** modes
- **Auto-paste** into the active window via clipboard or simulated keystrokes
- **Multi-language** -- English, Spanish, Mandarin, Japanese, Korean, Vietnamese, Arabic, Ukrainian, French, German, Portuguese, Russian, Italian
- **Model selection** -- Distil-Whisper (English-optimized), Large v3 Turbo, Medium, Small, Base, Tiny, Large v3
- **GPU acceleration** -- uses CUDA when available (NVIDIA GPUs), falls back to CPU gracefully
- **English-optimized default** -- ships with Distil-Large-v3 (6x faster than Large v3, <1% accuracy loss)

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
2. Pre-load the Distil-Large-v3 model in the background (~1.5 GB, cached in `D:\EkhoModels` after first download)
3. Wait for you to press **Ctrl+Shift+Space**

### How to dictate

1. Click into the app where you want text (Word, browser, Notepad, etc.)
2. Press **Ctrl+Shift+Space** -- a floating bar appears saying "Listening..."
3. Speak naturally, pause ~1-2 seconds between phrases
4. The overlay updates with your transcribed words
5. Press **Ctrl+Shift+Space** again to stop -- text is pasted into the focused app

## System Tray Menu

Right-click the tray icon for:
- **Start/Stop Listening** -- toggle dictation (same as hotkey)
- **Model** -- switch between Distil (English), Turbo, Medium, Small, Base, Tiny, Large v3
- **Hotkey Mode** -- switch between toggle and hold-to-talk
- **Paste Mode** -- clipboard paste (fast) or simulated typing
- **Language** -- switch transcription language
- **Show Overlay** -- toggle the floating preview bar
- **Quit** -- exit the app

## Configuration

Settings are saved to `%APPDATA%\Ekho\settings.json` and persist across sessions.

| Setting | Default | Description |
|---------|---------|-------------|
| `hotkey` | `ctrl+shift+space` | Global hotkey combo |
| `hotkey_mode` | `toggle` | `toggle` or `hold` |
| `model_size` | `distil-large-v3` | Whisper model (see Model menu for full list) |
| `language` | `en` | Two-letter language code |
| `auto_paste` | `true` | Use clipboard paste vs simulated typing |
| `overlay_enabled` | `true` | Show floating transcription bar |
| `overlay_opacity` | `0.85` | Overlay window opacity |
| `overlay_font_size` | `14` | Overlay text size |

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
Ekho/
  SOUL.md              -- agent identity & standards
  AGENTS.md            -- workflow rules for this repo
  README.md            -- this file
  CHANGELOG.md         -- timestamped release notes
  ROADMAP.md           -- planned features & milestones
  TODO.md              -- manual steps for Daniel
  requirements.txt     -- Python dependencies
  run.py               -- top-level launcher
  Ekho.spec            -- PyInstaller config
  build.ps1            -- build script for standalone .exe
  src/
    __init__.py
    __main__.py         -- python -m src support
    main.py             -- entry point, wires all modules
    settings.py         -- config persistence (%AppData%\Ekho)
    transcriber.py      -- faster-whisper wrapper with energy-based VAD
    audio.py            -- microphone device enumeration
    overlay.py          -- floating transcription preview (tkinter)
    hotkey.py           -- global hotkey listener
    injector.py         -- text injection into active app
    tray.py             -- system tray icon & menu
  assets/
    icon_64.png         -- tray icon (full brightness)
    icon_64_active.png  -- tray icon (active/listening)
    icon_64_inactive.png -- tray icon (dimmed/idle)
    ekho.ico            -- Windows .ico for packaged .exe
  logo/
    echo_logo.svg       -- project logo (waveform, cyan-to-green gradient)
```

## Building a Standalone .exe

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

The executable will be at `dist\Ekho.exe`. To start automatically with Windows, copy it to your Startup folder:

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
- sounddevice + numpy (audio capture and processing)
- Target: Windows 10/11

## Changelog

For timestamped release notes, see `CHANGELOG.md`.
