# TODO -- Manual Steps

Things Daniel needs to do that can't be automated by the agent.

## First Run
- [x] Create a virtual environment: `python -m venv venv`
- [x] Activate it: `venv\Scripts\activate`
- [x] Install deps: `pip install -r requirements.txt`
- [x] Install CUDA Toolkit 12.9: `winget install Nvidia.CUDA --version 12.9`
- [x] Run: `python run.py` -- first run downloads the Whisper model (~1.5 GB for medium).
- [x] Grant microphone permissions if Windows prompts.
- [x] Verify dictation works: Alt+Q, speak, pause, Alt+Q, text appears in focused app.

## Git Setup
- [x] `git init` in `D:\Vibe Coding\Eqho`
- [x] `git add .` and initial commit
- [x] Create GitHub repo (e.g. `gh repo create DanielMevit/Eqho --private --source . --remote origin --push`)

## Optional
- [ ] To add to Windows startup: copy `dist\Eqho.exe` to `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` (or use the "Start with Windows" toggle in the tray menu).
- [x] Test with your preferred microphone — mic selector available in tray menu since v0.2.0.

## Public Launch (Phase 5 -- do last)
- [ ] Pick a license (MIT, Apache 2.0, etc.)
- [ ] Move internal docs (SOUL.md, AGENTS.md, ROADMAP.md, TODO.md) out of the public repo or into a `.private/` folder in `.gitignore`
- [ ] Write a public-facing README with screenshots and a demo GIF
- [ ] Build a release binary and upload to GitHub Releases
- [ ] Flip the repo from private to public
