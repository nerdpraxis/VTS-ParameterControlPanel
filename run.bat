@echo off
REM VTS Control Panel - Run Script
echo Starting VTS Control Panel...
cd /d "%~dp0"
..\venv_py311\Scripts\python.exe main.py
pause
