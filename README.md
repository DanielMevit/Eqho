# Echo

**Your voice, everywhere.**

An always-on dictation app that runs in your system tray. Press a hotkey, speak, and your words are typed into whatever application is focused. Powered by [Moonshine Voice](https://github.com/moonshine-ai/moonshine) -- a fast, accurate, on-device speech-to-text engine.

## Features

- **Real-time transcription** -- see words appear as you speak via a floating overlay
- **100% local** -- no cloud, no API keys, everything runs on your machine
- **System tray** -- runs silently in the background
- **Global hotkey** -- works in any application (default: `Ctrl+Shift+Space`)
- **Toggle or hold-to-talk** modes
- **Auto-paste** into the active window via clipboard or simulated keystrokes
- **Multi-language** -- English, Spanish, Mandarin, Japanese, Korean, Vietnamese, Arabic, Ukrainian
- **CPU-friendly** -- runs on CPU by default, no GPU required

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
1. Appear as a microphone icon in your system tray
2. Pre-load the Moonshine model in the background (~200 MB, cached after first run)
3. Wait for you to press **Ctrl+Shift+Space**

When you press the hotkey, speak naturally. The overlay shows real-time transcription. Press the hotkey again to stop -- your words are automatically pasted into the focused app.

## System Tray Menu

Right-click the tray icon for:
- **Start/Stop Listening** -- toggle dictation (same as hotkey)
- **Hotkey Mode** -- switch between toggle and hold-to-talk
- **Paste Mode** -- clipboard paste (fast) or simulated typing
- **Language** -- switch transcription language
- **Show Overlay** -- toggle the floating preview bar
- **Quit** -- exit the app

## Configuration

Settings are saved to `%APPDATA%\Echo\settings.json` and persist across sessions.

| Setting | Default | Description |
|---------|---------|-------------|
| `hotkey` | `ctrl+shift+space` | Global hotkey combo |
| `hotkey_mode` | `toggle` | `toggle` or `hold` |
| `language` | `en` | Two-letter language code |
| `auto_paste` | `true` | Use clipboard paste vs simulated typing |
| `overlay_enabled` | `true` | Show floating transcription bar |
| `overlay_opacity` | `0.85` | Overlay window opacity |
| `overlay_font_size` | `14` | Overlay text size |

## Structure

```
Echo/
  SOUL.md              -- agent identity & standards
  AGENTS.md            -- workflow rules for this repo
  README.md            -- this file
  CHANGELOG.md         -- timestamped release notes
  ROADMAP.md           -- planned features & milestones
  TODO.md              -- manual steps for Daniel
  requirements.txt     -- Python dependencies
  run.py               -- top-level launcher
  Echo.spec            -- PyInstaller config
  build.ps1            -- build script for standalone .exe
  src/
    __init__.py
    __main__.py         -- python -m src support
    main.py             -- entry point, wires all modules
    settings.py         -- config persistence (%AppData%\Echo)
    transcriber.py      -- Moonshine Voice wrapper
    audio.py            -- microphone device enumeration
    overlay.py          -- floating transcription preview (tkinter)
    hotkey.py           -- global hotkey listener
    injector.py         -- text injection into active app
    tray.py             -- system tray icon & menu
  assets/
    (reserved for icons)
```

## Building a Standalone .exe

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

The executable will be at `dist\Echo.exe`. To start automatically with Windows, copy it to your Startup folder:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## Tech

- Python 3.10+
- Moonshine Voice (MIT license, on-device, CPU-friendly)
- pystray + Pillow (system tray)
- keyboard (global hotkeys)
- pynput + pyperclip (text injection)
- tkinter (overlay)
- sounddevice (audio device enumeration)
- Target: Windows 10/11

## Changelog

For timestamped release notes, see `CHANGELOG.md`.
