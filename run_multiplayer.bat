@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Python virtual environment was not found.
    echo Expected: .venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" tools\run_multiplayer.py

if errorlevel 1 (
    echo.
    echo Multiplayer launcher stopped with an error.
    pause
)

endlocal
