@echo off
echo Building VTS Control Panel executable...

REM Activate virtual environment
call ..\venv_py311\Scripts\activate.bat

REM Install PyInstaller if not already installed
pip install pyqtgraph numpy

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable with spec file...

REM Build using spec file
pyinstaller VTS-Control-Panel.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build failed! Check error messages above.
    pause
    exit /b 1
)

REM Copy necessary files to dist
copy config.ini.example dist\config.ini 2>nul
copy README.md dist\ 2>nul

echo.
echo Build complete! Check the 'dist' folder for VTS-Control-Panel.exe
echo.
pause
