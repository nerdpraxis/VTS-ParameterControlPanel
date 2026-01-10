@echo off
REM Development runner for VTS Control Panel
REM Runs the app from source using the Python virtual environment

echo Starting VTS Control Panel (Development Mode)...
cd /d "%~dp0"
"..\venv_py311\Scripts\python.exe" main.py
pause
