# Changelog

All notable changes to Ekho are tracked here.

Date format: `YYYY-MM-DD`.

## [0.1.4] - 2026-03-30

### Fixed
- Hotkey mode switching (toggle ↔ hold) no longer crashes the app. Replaced `keyboard.unhook_all()` with targeted hook removal.
- Text injection now pastes into the correct window (e.g. Word, browser) instead of the PowerShell terminal. Captures the foreground window handle on activation and restores focus before pasting.
- Modifier key release before paste — explicitly releases all modifier keys before simulating Ctrl+V to prevent ghost key conflicts.

### Changed
- Default hotkey changed from `Ctrl+Shift+Space` to **`Ctrl+Alt+D`** (D for Dictate). Space in the combo was interfering with normal typing.
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
- Removed Whisper's built-in `vad_filter` from transcribe calls -- it was too aggressive and discarding valid speech. Ekho's own energy-based VAD handles speech/silence detection.
- Lowered silence threshold from 0.01 to 0.003 RMS so quieter microphones are detected properly.
- Overlay now updates on completed segments (previously only updated on partials, so short phrases showed "Listening..." forever).
- Partial transcription now triggers every 1.5s of active speech (previously used a broken even-second-only check that rarely fired).
- Silenced noisy debug logging from PIL, httpx, httpcore, and huggingface_hub.

### Added
- Mic level diagnostic logging every 10 seconds while recording (RMS, peak, threshold, speaking state).
- CUDA Toolkit 12.9 added as a prerequisite for GPU acceleration (RTX 3060 verified working).

## [0.1.1] - 2026-03-30

### Changed
- Renamed project from Echo to **Ekho**.
- Updated all documentation to reflect faster-whisper (Whisper) as the transcription engine (replacing earlier Moonshine references).
- Updated tray icon to use the project logo instead of programmatic fallback.
- Updated config paths: `%AppData%\Ekho`, `D:/EkhoModels`.

## [0.1.0] - 2026-03-29

### Added
- Initial project scaffold with full dictation pipeline.
- faster-whisper integration for real-time speech-to-text (on-device, GPU + CPU, MIT license).
- System tray app with right-click menu: start/stop listening, model selection, hotkey mode, paste mode, language selection, overlay toggle, quit.
- Global hotkey support (`Ctrl+Shift+Space` default) with toggle and hold-to-talk modes.
- Floating overlay bar at screen bottom showing live partial transcription.
- Text injection into the active window via clipboard paste or simulated keystrokes.
- Settings persistence to `%AppData%\Ekho\settings.json` across sessions.
- Audio device enumeration via sounddevice.
- Multi-language support: 13 languages.
- Model selection: Tiny, Base, Small, Medium, Large v3.
- PyInstaller packaging support (`Ekho.spec` + `build.ps1`) for standalone `.exe`.
- Energy-based VAD for speech/silence detection with configurable thresholds.
