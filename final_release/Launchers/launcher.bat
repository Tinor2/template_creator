@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Opening Microsoft Store for installation...
    
    :: Open Microsoft Store for Python
    start ms-windows-store://pdp/?productid=9NJ46SX7X90P
    
    echo Please install Python from the Microsoft Store and run this launcher again.
    echo Installation will continue once you have installed Python.
    pause
    exit /b 1
)

:: Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Installing pip...
    python -m ensurepip --upgrade
)

:: Upgrade pip to latest version
python -m pip install --upgrade pip

:: Install required modules
python -m pip install -r requirements.txt

:: Run the main script
python Main/gui.py

endlocal
