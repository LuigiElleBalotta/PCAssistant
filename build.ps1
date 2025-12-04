# PC Assistant - Build Script (PowerShell Wrapper)
# Activates virtual environment and runs the Python build script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PC Assistant - Build System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

# Run build script
Write-Host ""
python build.py

# Wait for user
Write-Host ""
Read-Host "Press Enter to exit"

# Deactivate
deactivate
