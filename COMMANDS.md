# Eqho Commands Reference

All commands run from PowerShell in `D:\Vibe Coding\Eqho`.

## Daily Use

```powershell
# Navigate to project
cd "D:\Vibe Coding\Eqho"

# Activate virtual environment
venv\Scripts\activate

# Run the app
python run.py
```

## First-Time Setup

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## If venv breaks (e.g. after folder rename)

```powershell
# Delete and recreate
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Install / Update Dependencies

```powershell
venv\Scripts\activate
pip install -r requirements.txt
```

## Build Standalone .exe

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
# Output: dist\Eqho.exe
```

## Git

```powershell
# Check status
git status

# Add and commit
git add .
git commit -m "description of changes"

# Push to GitHub
git push origin main
```

## CUDA (GPU acceleration)

```powershell
# Install CUDA Toolkit 12.9 (one-time)
winget install Nvidia.CUDA --version 12.9
# Restart terminal after install
```

## Verify Windows Startup Registry

```powershell
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v Eqho
```

## Troubleshooting

```powershell
# Check Python version (need 3.10+)
python --version

# Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# Check installed packages
pip list

# Reinstall a specific package
pip install --force-reinstall customtkinter
```
