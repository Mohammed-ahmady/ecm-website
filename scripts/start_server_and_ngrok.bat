@echo off
REM =========================================
REM   🚀 ECM Website - Django + ngrok Launcher
REM =========================================

echo.
echo =========================================
echo   Starting Django server and ngrok tunnel
echo =========================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.x and try again.
    pause
    exit /b 1
)

REM Check ngrok
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: ngrok is not installed or not in PATH.
    echo Please install ngrok from https://ngrok.com/download
    pause
    exit /b 1
)

REM Set ngrok authtoken (idempotent)
echo Setting ngrok authtoken (safe to repeat)...
ngrok config add-authtoken 2zr6YzMk6Huam437tObcfDTJLDB_3RNvNej43dJCXnwZBMpsE >nul 2>nul

REM Start Django server in a new window
echo Launching Django development server on port 8000...
start "Django Server" cmd /k "python manage.py runserver 8000"

REM Wait for Django to start
set WAIT_TIME=7
echo Waiting %WAIT_TIME% seconds for Django to start...
ping 127.0.0.1 -n %WAIT_TIME% >nul

REM Start ngrok with custom domain
echo Launching ngrok tunnel with reserved domain...
set NGROK_DOMAIN=cowbird-advanced-infinitely.ngrok-free.app
ngrok http --domain=%NGROK_DOMAIN% 8000

echo.
echo =========================================
echo   Both servers have stopped. Goodbye!
echo =========================================
pause 