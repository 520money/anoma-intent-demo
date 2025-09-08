@echo off
setlocal

REM Ensure we are in the script directory
cd /d "%~dp0"

REM Create venv if missing
if not exist .venv (
    echo Creating virtual environment...
    py -3 -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install build deps
py -3 -m pip install --upgrade pip >NUL 2>&1
py -3 -m pip install -r requirements.txt
py -3 -m pip install pyinstaller

REM Build the exe with PyInstaller
py -3 -m PyInstaller --noconfirm --onefile --name IntentDemo app_main.py
py -3 -m PyInstaller --noconfirm --onefile --name IntentDemoGUI app_gui_main.py

echo.
echo Build complete. EXEs are at: dist\IntentDemo.exe and dist\IntentDemoGUI.exe
pause

endlocal

