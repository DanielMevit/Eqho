# Build Echo into a standalone .exe
# Run from the Echo directory:
#   powershell -ExecutionPolicy Bypass -File build.ps1

Write-Host "=== Building Echo ===" -ForegroundColor Cyan

pip install pyinstaller --quiet

pyinstaller Echo.spec --noconfirm

Write-Host ""
Write-Host "Build complete! Executable is at:" -ForegroundColor Green
Write-Host "  dist\Echo.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "To add to Windows startup:" -ForegroundColor Cyan
Write-Host '  Copy dist\Echo.exe to %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup' -ForegroundColor Yellow
