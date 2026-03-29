# Changelog

All notable changes to Echo are tracked here.

Date format: `YYYY-MM-DD`.

## [0.1.0] - 2026-03-29

### Added
- Initial project scaffold with full dictation pipeline.
- Moonshine Voice integration for real-time streaming speech-to-text (on-device, CPU-friendly, MIT license).
- System tray app with right-click menu: start/stop listening, hotkey mode, paste mode, language selection, overlay toggle, quit.
- Global hotkey support (`Ctrl+Shift+Space` default) with toggle and hold-to-talk modes.
- Floating overlay bar at screen bottom showing live partial transcription.
- Text injection into the active window via clipboard paste or simulated keystrokes.
- Settings persistence to `%AppData%\Echo\settings.json` across sessions.
- Audio device enumeration via sounddevice.
- Multi-language support: English, Spanish, Mandarin, Japanese, Korean, Vietnamese, Arabic, Ukrainian.
- PyInstaller packaging support (`Echo.spec` + `build.ps1`) for standalone `.exe`.
- Programmatic tray icon generation (microphone glyph, Catppuccin palette, active/inactive states).

### Verification
- All dependencies install cleanly (`pip install -r requirements.txt`).
- All module imports verified successfully.
- Moonshine Voice `MicTranscriber` API confirmed: `add_listener`, `remove_listener`, `start`, `stop`, `close`.
