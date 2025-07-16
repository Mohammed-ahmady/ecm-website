# Django Memory Management Script
# This script helps prevent VS Code crashes when running Django with ngrok

param(
    [switch]$CheckMemory,
    [switch]$CleanUp,
    [switch]$StartOptimized,
    [switch]$StopAll
)

function Show-MemoryUsage {
    Write-Host "=== System Memory Status ===" -ForegroundColor Cyan
    $memory = Get-WmiObject -Class Win32_OperatingSystem
    $totalMemGB = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $freeMemGB = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $usedMemGB = $totalMemGB - $freeMemGB
    $usagePercent = [math]::Round(($usedMemGB / $totalMemGB) * 100, 2)
    
    Write-Host "Total Memory: $totalMemGB GB" -ForegroundColor White
    Write-Host "Used Memory: $usedMemGB GB ($usagePercent%)" -ForegroundColor $(if($usagePercent -gt 80) {"Red"} elseif($usagePercent -gt 60) {"Yellow"} else {"Green"})
    Write-Host "Free Memory: $freeMemGB GB" -ForegroundColor Green
    
    if($usagePercent -gt 80) {
        Write-Host "⚠️  HIGH MEMORY USAGE DETECTED!" -ForegroundColor Red
        Write-Host "Consider closing other applications before running Django." -ForegroundColor Yellow
    }
}

function Stop-DjangoProcesses {
    Write-Host "Stopping Django processes..." -ForegroundColor Yellow
    
    # Stop Python processes running Django
    Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "pythonw"} | ForEach-Object {
        try {
            $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            if($commandLine -like "*manage.py*" -or $commandLine -like "*runserver*") {
                Write-Host "Stopping Django process: $($_.Id)" -ForegroundColor Red
                Stop-Process -Id $_.Id -Force
            }
        } catch {
            # Process might have already stopped
        }
    }
    
    # Stop ngrok if requested
    if($StopAll) {
        Get-Process | Where-Object {$_.ProcessName -eq "ngrok"} | ForEach-Object {
            Write-Host "Stopping ngrok process: $($_.Id)" -ForegroundColor Red
            Stop-Process -Id $_.Id -Force
        }
    }
}

function Start-DjangoOptimized {
    Write-Host "Starting Django with memory optimizations..." -ForegroundColor Green
    
    # Set environment variables for optimization
    $env:PYTHONOPTIMIZE = "1"
    $env:PYTHONDONTWRITEBYTECODE = "1"
    
    # Clean up first
    Stop-DjangoProcesses
    
    # Start Django with memory-friendly options
    Start-Process python -ArgumentList "manage.py", "runserver", "127.0.0.1:8000", "--noreload" -Wait
}

function Clean-TempFiles {
    Write-Host "Cleaning temporary files..." -ForegroundColor Yellow
    
    # Clean Python cache files
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    
    # Clean Django temporary files
    if(Test-Path "db.sqlite3-journal") { Remove-Item "db.sqlite3-journal" -Force }
    
    # Clean VS Code temp files
    if(Test-Path ".vscode\.ropeproject") { Remove-Item ".vscode\.ropeproject" -Recurse -Force -ErrorAction SilentlyContinue }
    
    Write-Host "✅ Cleanup completed!" -ForegroundColor Green
}

# Main script logic
Write-Host "Django Memory Management Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if($CheckMemory) {
    Show-MemoryUsage
}

if($CleanUp) {
    Clean-TempFiles
}

if($StopAll) {
    Stop-DjangoProcesses
}

if($StartOptimized) {
    Show-MemoryUsage
    Clean-TempFiles
    Start-DjangoOptimized
}

if(-not ($CheckMemory -or $CleanUp -or $StartOptimized -or $StopAll)) {
    Write-Host "Usage examples:" -ForegroundColor Yellow
    Write-Host "  .\manage_memory.ps1 -CheckMemory     # Check system memory" -ForegroundColor White
    Write-Host "  .\manage_memory.ps1 -CleanUp         # Clean temporary files" -ForegroundColor White
    Write-Host "  .\manage_memory.ps1 -StartOptimized  # Start Django optimized" -ForegroundColor White
    Write-Host "  .\manage_memory.ps1 -StopAll         # Stop all processes" -ForegroundColor White
}
