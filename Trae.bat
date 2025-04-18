@echo off
title Trae
echo Checking for required dependencies...

:: Check if pip is installed
where pip >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: pip is not installed or not in PATH
    echo Please install Python with pip and try again
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
pip install SpeechRecognition
pip install pyaudio
pip install pywin32

echo Starting conversation service...
python H:\VSCodeProjects\HumanAI\python\conversation.py
pause