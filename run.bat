@echo off
REM PC Assistant - Quick Launcher
REM Automatically activates virtual environment and runs the application

echo ========================================
echo   PC Assistant - System Cleaner
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo.
echo Starting PC Assistant...
echo.
python src\main.py

REM Deactivate on exit
deactivate
