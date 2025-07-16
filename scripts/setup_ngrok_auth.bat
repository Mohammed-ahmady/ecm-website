@echo off
echo.
echo ========================================
echo       ngrok Authentication Setup
echo ========================================
echo.
echo Please paste your ngrok auth token when prompted.
echo You can find it at: https://dashboard.ngrok.com/get-started/your-authtoken
echo.
set /p TOKEN="2zr6YzMk6Huam437tObcfDTJLDB_3RNvNej43dJCXnwZBMpsE"
echo.
echo Setting up ngrok authentication...
"%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" config add-authtoken %TOKEN%
echo.
echo ✅ Authentication setup complete!
echo.
echo You can now run start_ngrok.bat to start your tunnel
echo.
pause
