# Build Ekho into a standalone .exe
# Run from the Ekho directory:
#   powershell -ExecutionPolicy Bypass -File build.ps1

Write-Host "=== Building Ekho ===" -ForegroundColor Cyan

pip install pyinstaller --quiet

pyinstaller Ekho.spec --noconfirm

Write-Host ""
Write-Host "Build complete! Executable is at:" -ForegroundColor Green
Write-Host "  dist\Ekho.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "To add to Windows startup:" -ForegroundColor Cyan
Write-Host '  Copy dist\Ekho.exe to %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup' -ForegroundColor Yellow
