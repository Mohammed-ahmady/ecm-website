# PowerShell script to fix SECRET_KEY in .env file
# Run this if you see the security.W009 warning about SECRET_KEY

function Generate-SecretKey {
    param (
        [int]$Length = 64
    )
    
    # Generate a secure random string using .NET
    $random = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    $bytes = New-Object byte[]($Length)
    $random.GetBytes($bytes)
    
    # Convert to Base64 and remove special characters that might cause issues
    $key = [Convert]::ToBase64String($bytes) -replace '\+', 'a' -replace '/', 'b' -replace '=', 'c'
    
    # Ensure the key is the right length
    if ($key.Length -gt $Length) {
        $key = $key.Substring(0, $Length)
    }
    
    return $key
}

function Update-EnvFile {
    # Get the path to the .env file
    $scriptPath = $MyInvocation.MyCommand.Path
    $scriptDir = Split-Path -Path $scriptPath -Parent
    $projectRoot = Split-Path -Path $scriptDir -Parent
    $envPath = Join-Path -Path $projectRoot -ChildPath ".env"
    
    if (-not (Test-Path $envPath)) {
        Write-Host "❌ No .env file found at $envPath" -ForegroundColor Red
        return
    }
    
    # Read the current content
    $envContent = Get-Content -Path $envPath -Raw
    
    # Generate a new secure key
    $newSecretKey = Generate-SecretKey
    
    # Check if SECRET_KEY already exists in the file
    if ($envContent -match 'SECRET_KEY=.+') {
        # Replace the existing SECRET_KEY
        $updatedContent = $envContent -replace 'SECRET_KEY=.+', "SECRET_KEY=$newSecretKey"
    } else {
        # Add SECRET_KEY if it doesn't exist
        $updatedContent = $envContent + "`nSECRET_KEY=$newSecretKey`n"
    }
    
    # Write the updated content back to the file
    Set-Content -Path $envPath -Value $updatedContent
    
    Write-Host "✅ SECRET_KEY has been updated in .env file" -ForegroundColor Green
    Write-Host "New SECRET_KEY: $newSecretKey" -ForegroundColor Cyan
    Write-Host "Length: $($newSecretKey.Length) characters" -ForegroundColor Cyan
    Write-Host "Run 'python manage.py check --deploy' to confirm the warning is resolved."
}

# Run the update function
Update-EnvFile
