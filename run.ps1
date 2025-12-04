# PC Assistant - PowerShell Launcher
# Automatically activates virtual environment and runs the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PC Assistant - System Cleaner" -ForegroundColor Cyan
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

# Check if dependencies are installed
try {
    python -c "import PyQt5" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyQt5 not found"
    }
} catch {
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Run the application
Write-Host ""
Write-Host "Starting PC Assistant..." -ForegroundColor Green
Write-Host ""
python src\main.py

# Deactivate on exit
deactivate
