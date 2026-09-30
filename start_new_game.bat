@echo off
call "%~dp0start_gui.bat" --new %*
exit /b %errorlevel%
