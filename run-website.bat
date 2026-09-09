@echo off
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python server.py
    goto :eof
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 server.py
    goto :eof
)

echo Python is required to run this website locally.
echo Please install Python 3 from https://www.python.org/downloads/
pause
