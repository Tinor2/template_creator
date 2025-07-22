@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Installing Python...
    
    :: Download and install Python
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python_installer.exe'"
    
    :: Run Python installer
    start /wait python_installer.exe /quiet /passive
    
    :: Clean up
    del python_installer.exe
    
    echo Python installation complete
)

:: Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Installing pip...
    python -m ensurepip --upgrade
)

:: Install required modules
python -m pip install -r requirements.txt

:: Run the main script
python Main/gui.py

endlocal
