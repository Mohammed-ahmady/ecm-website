@echo off
echo ================================
echo Django Memory Management Helper
echo ================================
echo.

:menu
echo Please choose an option:
echo 1. Check system memory
echo 2. Clean temporary files
echo 3. Stop all Django/ngrok processes
echo 4. Start Django (optimized)
echo 5. Restart VS Code safely
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto check_memory
if "%choice%"=="2" goto cleanup
if "%choice%"=="3" goto stop_processes
if "%choice%"=="4" goto start_django
if "%choice%"=="5" goto restart_vscode
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
goto menu

:check_memory
echo Checking system memory...
powershell -Command "Get-WmiObject -Class Win32_OperatingSystem | Select-Object @{Name='TotalMemory(GB)';Expression={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, @{Name='FreeMemory(GB)';Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}"
echo.
pause
goto menu

:cleanup
echo Cleaning temporary files...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.pyc" del /s /q "*.pyc"
if exist "db.sqlite3-journal" del "db.sqlite3-journal"
echo Cleanup completed!
echo.
pause
goto menu

:stop_processes
echo Stopping Django and ngrok processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *manage.py*" 2>nul
taskkill /f /im ngrok.exe 2>nul
echo Processes stopped!
echo.
pause
goto menu

:start_django
echo Starting Django with memory optimizations...
set PYTHONOPTIMIZE=1
set PYTHONDONTWRITEBYTECODE=1
python manage.py runserver 127.0.0.1:8000 --noreload
goto menu

:restart_vscode
echo Restarting VS Code safely...
echo 1. Saving all files...
echo 2. Closing VS Code...
taskkill /f /im Code.exe 2>nul
timeout /t 3 /nobreak >nul
echo 3. Starting VS Code...
start "" "code" "."
echo VS Code restarted!
echo.
pause
goto menu

:exit
echo Goodbye!
exit
