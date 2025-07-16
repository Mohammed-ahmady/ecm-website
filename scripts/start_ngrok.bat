@echo off
echo.
echo ========================================
echo    🚀 ECM Website - ngrok Tunnel
echo ========================================
echo.

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: ngrok is not installed or not in PATH
    echo Please install ngrok from https://ngrok.com/download
    pause
    exit /b 1
)

echo Starting ngrok tunnel to Django server...
echo Your Django server should be running on http://127.0.0.1:8000
echo.
echo 🌐 Your website will be accessible worldwide!
echo.
echo Setting up ngrok configuration...
ngrok config add-authtoken 2zr6YzMk6Huam437tObcfDTJLDB_3RNvNej43dJCXnwZBMpsE

echo Starting tunnel with custom domain...
set NGROK_ARGS=http --domain=cowbird-advanced-infinitely.ngrok-free.app --log=stdout --log-format=json --log-level=info 8000

REM Try different methods to start ngrok
if exist "%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" (
    "%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" %NGROK_ARGS%
) else (
    where ngrok >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        ngrok %NGROK_ARGS%
    ) else (
        echo Error: ngrok not found. Please install ngrok and try again.
        pause
        exit /b 1
    )
)

echo.
echo Tunnel stopped. Press any key to exit...
pause
