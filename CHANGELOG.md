# Changelog

All notable changes to Eqho are tracked here.

Date format: `YYYY-MM-DD`.

## [0.2.0] - 2026-03-31

### Changed
- **Renamed project from Ekho to Eqho.** Updated all code, docs, config paths, and build scripts.
- Default hotkey changed to **`Alt+Q`** (Q for Eqho). Single left-hand combo, no conflicts.
- Default mic set to Realtek Mic Array (device 3) to avoid Bluetooth HFP profile switching.
- Default volume duck set to **Mute** while speaking.
- Config paths: `%AppData%\Eqho`, `D:\EqhoModels`.

### Added
- **Microphone selector** in tray menu — pick which mic to use for dictation.
- **Volume While Speaking** option in tray menu — Off, 50%, 25%, 10%, or Mute. Silently controls system volume via Windows Core Audio API (pycaw).
- Emergency unmute on app exit via `atexit` — system audio is never left muted if Eqho crashes or is force-closed.
- `pycaw` dependency for silent programmatic volume control.

### Fixed
- Hold mode no longer cuts off the last word. Worker thread drains audio queue and flushes before mic closes.
- Hotkey mode switching (toggle ↔ hold) no longer crashes. Rewrote hold mode to use a single `keyboard.hook()` to avoid the library's internal hook corruption bug.
- Toggle mode no longer double-fires. Added 400ms debounce.
- Settings changes (hotkey mode, paste mode) skip unnecessary model reloads.
- Volume control uses COM per-thread initialization to work from hotkey callback threads.

## [0.1.4] - 2026-03-30

### Fixed
- Text injection now pastes into the correct window (e.g. Word, browser) instead of the PowerShell terminal. Captures the foreground window handle on activation and restores focus before pasting.
- Modifier key release before paste — explicitly releases all modifier keys before simulating Ctrl+V to prevent ghost key conflicts.

### Changed
- Increased post-dictation delay (0.15s → 0.4s) to allow modifier keys to fully release before paste injection.

## [0.1.3] - 2026-03-30

### Changed
- Default model switched from `medium` to **`distil-large-v3`** (English-optimized, ~6x faster than large-v3 with <1% accuracy loss).
- Model menu reorganized: Distil models (English-optimized) listed first, then multilingual models (Turbo, Medium, Small, Base, Tiny, Large v3).
- CUDA device picker now routes all models except `large-v3` to GPU (distil and turbo models fit easily in 6GB VRAM).
- Roadmap updated: Phase 4 is now whisper.cpp migration for native distribution (replacing Python/faster-whisper for the commercial release).

### Added
- New models available in tray menu: `distil-large-v3`, `distil-medium.en`, `distil-small.en`, `large-v3-turbo`.

## [0.1.2] - 2026-03-30

### Fixed
- CUDA inference now falls back to CPU gracefully when `cublas64_12.dll` is missing. A smoke test runs at model load time instead of failing at first transcription.
- Removed Whisper's built-in `vad_filter` from transcribe calls -- it was too aggressive and discarding valid speech. Eqho's own energy-based VAD handles speech/silence detection.
- Lowered silence threshold from 0.01 to 0.003 RMS so quieter microphones are detected properly.
- Overlay now updates on completed segments (previously only updated on partials, so short phrases showed "Listening..." forever).
- Partial transcription now triggers every 1.5s of active speech (previously used a broken even-second-only check that rarely fired).
- Silenced noisy debug logging from PIL, httpx, httpcore, and huggingface_hub.

### Added
- Mic level diagnostic logging every 10 seconds while recording (RMS, peak, threshold, speaking state).
- CUDA Toolkit 12.9 added as a prerequisite for GPU acceleration (RTX 3060 verified working).

## [0.1.1] - 2026-03-30

### Changed
- Renamed project from Echo to **Eqho**.
- Updated all documentation to reflect faster-whisper (Whisper) as the transcription engine (replacing earlier Moonshine references).
- Updated tray icon to use the project logo instead of programmatic fallback.
- Updated config paths: `%AppData%\Eqho`, `D:/EqhoModels`.

## [0.1.0] - 2026-03-29

### Added
- Initial project scaffold with full dictation pipeline.
- faster-whisper integration for real-time speech-to-text (on-device, GPU + CPU, MIT license).
- System tray app with right-click menu: start/stop listening, model selection, hotkey mode, paste mode, language selection, overlay toggle, quit.
- Global hotkey support (`Ctrl+Shift+Space` default) with toggle and hold-to-talk modes.
- Floating overlay bar at screen bottom showing live partial transcription.
- Text injection into the active window via clipboard paste or simulated keystrokes.
- Settings persistence to `%AppData%\Eqho\settings.json` across sessions.
- Audio device enumeration via sounddevice.
- Multi-language support: 13 languages.
- Model selection: Tiny, Base, Small, Medium, Large v3.
- PyInstaller packaging support (`Eqho.spec` + `build.ps1`) for standalone `.exe`.
- Energy-based VAD for speech/silence detection with configurable thresholds.
