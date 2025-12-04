@echo off
REM PC Assistant - Build Script (Batch Wrapper)
REM Activates virtual environment and runs the Python build script

echo ========================================
echo   PC Assistant - Build System
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

REM Run build script
echo.
python build.py

REM Pause to see results
echo.
pause

REM Deactivate
deactivate
