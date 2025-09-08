@echo off
setlocal

cd /d "%~dp0"

if not exist .venv (
    echo Creating virtual environment...
    py -3 -m venv .venv
)

call .venv\Scripts\activate.bat
py -3 -m pip install --upgrade pip >NUL 2>&1
py -3 -m pip install -r requirements.txt

echo Starting desktop GUI...
py -3 -m src.gui

endlocal

