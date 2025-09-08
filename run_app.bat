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

REM Install requirements
py -3 -m pip install --upgrade pip >NUL 2>&1
py -3 -m pip install -r requirements.txt

REM Start the web app
echo Starting app at http://127.0.0.1:5000 ...
py -3 -m src.web

endlocal

