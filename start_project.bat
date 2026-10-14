@echo off
title InterviewGPT Setup & Launch

echo ==========================================
echo InterviewGPT Setup and Launch
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1

if errorlevel 1 (
    echo Python not found.
    echo.
    echo Downloading Python installer...
    
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe -OutFile python_installer.exe"

    echo Installing Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    timeout /t 10 >nul
)

echo.
echo Creating virtual environment...

if not exist venv (
    python -m venv venv
)

echo.
echo Activating virtual environment...

call venv\Scripts\activate.bat

echo.
echo Upgrading pip...

python -m pip install --upgrade pip

echo.
echo Installing requirements...

pip install -r req.txt

echo.
echo Starting Streamlit App...

streamlit run app.py

pause