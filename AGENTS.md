# Codex rules for this repo (Echo)

## Reading ritual
- At session start, read SOUL.md, then AGENTS.md, then README.md silently and obey them.
- Do not summarize them unless Daniel explicitly asks.

## SOUL handling
- Treat SOUL.md as identity/standards. Update it only when those evolve (not as a task log).

## Workflow
- Don't ask for permission or micromanage. Plan, implement, run, summarize in one go.
- Work in milestone-sized steps: Plan -> implement -> run -> summarize.
- One task should deliver a visible improvement and include verification (run/test) and a CHANGELOG.md entry.
- Prefer minimal dependencies; justify each new one.
- Always verify changes work after making them (`python run.py` or import check at minimum).
- Do not modify anything outside this repository.
- Do not rename or change the folder structure. The project source lives in `src/`; that folder stays named `src`.

## Documentation
- CHANGELOG.md is the timestamped release log. Append every meaningful change with a `YYYY-MM-DD` header.
- README.md is the project overview only. Update feature lists and structure section when new modules are added. Do not add progress logs or session notes to README.
- ROADMAP.md tracks planned features and milestones. Update when priorities shift.
- TODO.md tracks manual steps Daniel needs to do. Keep it short and actionable.
- Keep entries concise. No long logs, no file lists.

## Architecture
- Python 3.10+, runs on Windows 10/11.
- Entry point: `run.py` (calls `src.main.main()`).
- Transcription engine: Moonshine Voice (`moonshine-voice` pip package, MIT license).
- Each responsibility lives in its own module inside `src/`:
  - `settings.py` -- config persistence (`%AppData%\Echo\settings.json`)
  - `transcriber.py` -- Moonshine Voice wrapper
  - `audio.py` -- device enumeration
  - `overlay.py` -- floating transcription preview (tkinter)
  - `hotkey.py` -- global hotkey (keyboard library)
  - `injector.py` -- text injection into active app (pynput + pyperclip)
  - `tray.py` -- system tray icon and menu (pystray + Pillow)
  - `main.py` -- wires everything together
- Settings persist in `%AppData%\Echo\settings.json`.

## Versioning
- Current version line: **v0.1.x** -- patch numbers increment freely.
- Tag releases as `vMAJOR.MINOR.PATCH` when publishing milestones.

## Commit & push
- Commit message format: `type(scope): short description` (conventional commits).
- Always push to `origin main` after a passing build/verification.
