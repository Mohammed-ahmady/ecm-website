@echo off
echo.
echo ========================================
echo    🚀 ECM Website - ngrok Tunnel
echo ========================================
echo.
echo Starting ngrok tunnel to Django server...
echo Your Django server should be running on http://127.0.0.1:8000
echo.
echo 🌐 Your website will be accessible worldwide!
echo.
echo Starting tunnel...
"%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http 8000
echo.
echo Tunnel stopped. Press any key to exit...
pause
