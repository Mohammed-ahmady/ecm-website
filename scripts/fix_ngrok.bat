@echo off
echo.
echo ========================================
echo    🔧 NGrok Troubleshooter
echo ========================================
echo.

echo Step 1: Checking ngrok installation...
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ngrok not found in PATH
    echo Installing ngrok via winget...
    winget install ngrok
) else (
    echo ngrok is installed
)

echo.
echo Step 2: Clearing ngrok configuration...
ngrok config delete-all

echo.
echo Step 3: Setting up authentication...
ngrok config add-authtoken 2zr6YzMk6Huam437tObcfDTJLDB_3RNvNej43dJCXnwZBMpsE

echo.
echo Step 4: Testing connection...
echo Testing connection to ngrok servers...
ping -n 1 app.ngrok.com
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Cannot reach ngrok servers
    echo Please check your internet connection or proxy settings
) else (
    echo Successfully reached ngrok servers
)

echo.
echo Step 5: Testing DNS resolution...
nslookup cowbird-advanced-infinitely.ngrok-free.app
if %ERRORLEVEL% NEQ 0 (
    echo Warning: DNS resolution failed
    echo This might affect the connection
) else (
    echo DNS resolution successful
)

echo.
echo ========================================
echo Troubleshooting complete!
echo.
echo If you still have issues:
echo 1. Try running ngrok with --verbose flag
echo 2. Check your firewall settings
echo 3. Try using a different network
echo 4. Make sure port 8000 is not blocked
echo ========================================
echo.
pause
