@echo off
echo Building VTS Control Panel executable...

REM Activate virtual environment
call ..\venv_py311\Scripts\activate.bat

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build executable
pyinstaller --name "VTS-Control-Panel" --onefile --windowed --add-data "README.md;." --hidden-import PyQt6 --hidden-import websockets --hidden-import pyqtgraph main.py

REM Copy necessary files to dist
copy config.ini.example dist\config.ini 2>nul
copy README.md dist\ 2>nul

echo.
echo Build complete! Check the 'dist' folder for VTS-Control-Panel.exe
echo.
pause
