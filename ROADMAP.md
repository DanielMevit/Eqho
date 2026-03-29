# Roadmap

Planned features and milestones for Echo.

## Phase 1 -- Core Dictation (v0.1.x) [done]
- [x] Moonshine Voice integration with streaming transcription
- [x] System tray with start/stop/quit
- [x] Global hotkey (toggle + hold-to-talk modes)
- [x] Floating overlay showing real-time partial text
- [x] Auto-paste into active window (clipboard + simulated typing)
- [x] Settings persistence to JSON
- [x] Multi-language support (8 languages)
- [x] PyInstaller packaging

## Phase 2 -- Polish & Reliability (v0.2.x) [next]
- [ ] Audio device selector in tray menu (pick which microphone)
- [ ] Hotkey customization UI (press-to-capture in a settings window)
- [ ] Startup with Windows toggle (registry-based)
- [ ] Notification on model download progress (first run)
- [ ] Graceful error handling for missing microphone
- [ ] Overlay position preference (bottom-center, top-center, corner)
- [ ] Tray tooltip showing current hotkey and language

## Phase 3 -- Advanced Features (v0.3.x)
- [ ] Transcript history log (save past dictations to a local file)
- [ ] Voice commands (e.g. "new line", "period", "delete that")
- [ ] Per-application paste mode rules (some apps need typing, not clipboard)
- [ ] Sound feedback (subtle chime on start/stop)
- [ ] Intent recognition via Moonshine Voice IntentRecognizer

## Phase 4 -- Distribution & Ecosystem (v0.4.x)
- [ ] Signed Windows installer (MSIX or Inno Setup)
- [ ] Auto-update mechanism
- [ ] Plugin system for custom post-processing (e.g. punctuation cleanup, formatting)
- [ ] macOS support (pystray + different hotkey backend)
- [ ] REST API mode for integration with other tools

## Stretch Goals
- [ ] Speaker identification (who's talking)
- [ ] Real-time translation (transcribe in one language, output in another)
- [ ] System audio capture (transcribe meetings/calls, not just mic)
- [ ] Electron or Tauri GUI replacing tkinter overlay
