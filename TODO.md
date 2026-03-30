# TODO -- Manual Steps

Things Daniel needs to do that can't be automated by the agent.

## First Run
- [x] Create a virtual environment: `python -m venv venv`
- [x] Activate it: `venv\Scripts\activate`
- [x] Install deps: `pip install -r requirements.txt`
- [x] Install CUDA Toolkit 12.9: `winget install Nvidia.CUDA --version 12.9`
- [x] Run: `python run.py` -- first run downloads the Whisper model (~1.5 GB for medium).
- [ ] Grant microphone permissions if Windows prompts.
- [x] Verify dictation works: Ctrl+Shift+D, speak, pause, Ctrl+Shift+D, text appears in focused app.

## Git Setup
- [ ] `git init` in `D:\Vibe Coding\Ekho`
- [ ] `git add .` and initial commit
- [ ] Create GitHub repo (e.g. `gh repo create DanielMevit/Ekho --private --source . --remote origin --push`)

## Optional
- [ ] To add to Windows startup: copy `dist\Ekho.exe` to `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` (build the .exe first with `build.ps1`).
- [ ] Test with your preferred microphone -- right now it uses the system default. Audio device selection is planned for Phase 2.

## Public Launch (Phase 5 -- do last)
- [ ] Pick a license (MIT, Apache 2.0, etc.)
- [ ] Move internal docs (SOUL.md, AGENTS.md, ROADMAP.md, TODO.md) out of the public repo or into a `.private/` folder in `.gitignore`
- [ ] Write a public-facing README with screenshots and a demo GIF
- [ ] Build a release binary and upload to GitHub Releases
- [ ] Flip the repo from private to public
