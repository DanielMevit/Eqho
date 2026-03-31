# Roadmap

Planned features and milestones for Eqho.

## Phase 1 -- Core Dictation (v0.1.x) [done]
- [x] faster-whisper integration with energy-based VAD and streaming transcription
- [x] System tray with start/stop/quit
- [x] Global hotkey (toggle + hold-to-talk modes)
- [x] Floating overlay showing real-time partial text
- [x] Auto-paste into active window (clipboard + simulated typing)
- [x] Settings persistence to JSON
- [x] Multi-language support (13 languages)
- [x] Model selection (Tiny through Large v3, Distil models, Turbo)
- [x] PyInstaller packaging
- [x] CUDA GPU acceleration with automatic CPU fallback
- [x] Tray icon from project logo (active/inactive states)
- [x] Distil-Whisper as default (English-optimized, fastest high-quality model)

## Phase 2 -- Polish & Reliability (v0.2.x) [done]
- [x] Audio device selector in tray menu (pick which microphone)
- [x] Volume while speaking (mute/50%/25%/10%/off via pycaw)
- [x] Hotkey rewrite — hold mode uses keyboard.hook() to avoid library bug, toggle has 400ms debounce
- [x] Window focus capture/restore for correct paste target
- [x] Rename from Ekho to Eqho (code, docs, config paths, build scripts)
- [x] Hotkey customization UI (press-to-capture in a settings window)
- [x] Startup with Windows toggle (registry-based)
- [x] Notification on model download progress (first run)
- [x] Graceful error handling for missing microphone
- [x] Overlay position preference (bottom-center, top-center, corner)
- [x] Tray tooltip showing current hotkey and language
- [x] **Dashboard** — customtkinter settings window with sidebar nav, theme system, model cards, singleton behavior
- [x] **Inter font** bundled as standard app typeface
- [x] **Theme system** — dark, light, system (auto-detect from Windows registry)

## Phase 3 -- Advanced Features (v0.3.x)
- [ ] Transcript history log (save past dictations to a local file)
- [ ] Voice commands (e.g. "new line", "period", "delete that")
- [ ] Per-application paste mode rules (some apps need typing, not clipboard)
- [ ] Sound feedback (subtle chime on start/stop)
- [ ] Whisper prompt/prefix for domain-specific vocabulary

## Phase 4 -- whisper.cpp Migration & Native App (v0.4.x)
Migrate from Python + faster-whisper to a native engine for a clean, distributable product.
- [ ] Replace faster-whisper with **whisper.cpp** (C++ engine, zero Python dependency)
- [ ] Evaluate Tauri (Rust) or C#/WPF for the app shell (replacing tkinter overlay + pystray)
- [ ] Dynamic model download on first launch (keep installer small)
- [ ] Ship as a single lightweight installer (MSI, MSIX, or Inno Setup)
- [ ] Signed Windows binary
- [ ] Auto-update mechanism
- [ ] Plugin system for custom post-processing (e.g. punctuation cleanup, formatting)

### Why whisper.cpp for distribution
- Pure C/C++, no Python runtime, no 200MB+ PyInstaller bundle
- Runs fast on CPU out of the box; supports CUDA, DirectCompute, and Vulkan for GPU
- Native bindings for C#, Rust, Go, Node.js (Whisper.net for C#, whisper-rs for Rust)
- End-user experience: install and run, no venv, no pip, no CUDA Toolkit headaches
- Current faster-whisper stack is ideal for development velocity; whisper.cpp is for shipping

## Phase 5 -- Public Launch Prep (v1.0)
This is the final gate before going public. Internal .md files (SOUL, AGENTS, ROADMAP, TODO) stay private.
- [ ] Remove or relocate internal docs (SOUL.md, AGENTS.md, ROADMAP.md, TODO.md) from the public repo
- [ ] Write a clean public README with screenshots, feature highlights, and install instructions
- [ ] Create a GitHub Releases page with pre-built installer
- [ ] Add LICENSE file (pick license -- MIT, Apache 2.0, etc.)
- [ ] Add CONTRIBUTING.md if accepting community contributions
- [ ] Optional: simple landing page (GitHub Pages or standalone)
- [ ] Optional: demo GIF / video showing Eqho in action
- [ ] Final QA pass -- test on a clean Windows install
- [ ] Flip repo from private to public

## Stretch Goals
- [ ] Speaker identification (who's talking)
- [ ] Real-time translation (transcribe in one language, output in another)
- [ ] System audio capture (transcribe meetings/calls, not just mic)
- [ ] macOS support
- [ ] REST API mode for integration with other tools
