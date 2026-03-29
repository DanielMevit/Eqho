# TODO -- Manual Steps

Things Daniel needs to do that can't be automated by the agent.

## First Run
- [ ] Create a virtual environment: `python -m venv venv`
- [ ] Activate it: `venv\Scripts\activate`
- [ ] Install deps: `pip install -r requirements.txt`
- [ ] Run: `python run.py` -- the first run will download the Moonshine model (~200 MB). Keep the terminal open until it finishes.
- [ ] Grant microphone permissions if Windows prompts.

## Git Setup
- [ ] `git init` in `D:\Vibe Coding\Echo`
- [ ] `git add .` and initial commit
- [ ] Create GitHub repo (e.g. `gh repo create DanielMevit/Echo --private --source . --remote origin --push`)

## Optional
- [ ] To add to Windows startup: copy `dist\Echo.exe` to `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` (build the .exe first with `build.ps1`).
- [ ] Test with your preferred microphone -- right now it uses the system default. Audio device selection is planned for Phase 2.
