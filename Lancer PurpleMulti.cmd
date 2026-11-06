@echo off
rem Starts PurpleMulti. Account data stays outside the repository.
cd /d "%~dp0"
rem Fast when nothing changed; installs new dependencies after a merge with the original project.
uv sync --locked --quiet
if errorlevel 1 (
    if not exist ".venv\Scripts\pythonw.exe" (
        echo Installation failed. Check that uv is installed: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
    echo Dependencies could not be updated, starting with the installed ones.
)
set "RAM_DATA_DIR=%LOCALAPPDATA%\PurpleMulti"
start "" ".venv\Scripts\pythonw.exe" "src\main.py"
