@echo off
echo Building Screen Time Tracker...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Build the executable
echo.
echo Step 1: Building executable...
python build.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo.
echo Next steps:
echo 1. Install Inno Setup from https://jrsoftware.org/isinfo.php
echo 2. Open setup.iss in Inno Setup Compiler
echo 3. Build the installer (F9)
echo.
pause

