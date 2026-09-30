@echo off
setlocal
cd /d "%~dp0"
if not exist "chinese_checkers\gui.py" (
    echo Game files are missing. Extract the complete project first.
    pause
    exit /b 1
)
if not exist "pyproject.toml" (
    echo pyproject.toml is missing. Extract the complete project first.
    pause
    exit /b 1
)
set "python_command=py -3"
if exist ".venv\Scripts\python.exe" (
    set "python_command=.venv\Scripts\python.exe"
) else (
    py -3 --version >nul 2>&1
    if errorlevel 1 set "python_command=python"
)
%python_command% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if errorlevel 1 (
    echo Python 3.9 or later is required. Install Python and try again.
    pause
    exit /b 1
)
%python_command% -c "import pygame" >nul 2>&1
if errorlevel 1 (
    %python_command% -m pip install -e ".[gui]"
    if errorlevel 1 (
        echo Could not install the graphical requirements.
        pause
        exit /b 1
    )
)
%python_command% -m chinese_checkers.gui %*
set "game_exit_code=%errorlevel%"
if not "%game_exit_code%"=="0" pause
exit /b %game_exit_code%
