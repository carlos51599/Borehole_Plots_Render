# PowerShell script to diagnose Dash application network issues

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "    Dash Application Network Diagnostics" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# Check if ports are in use
function Test-PortInUse {
    param (
        [int]$port
    )
    
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $port)
        $listener.Start()
        $listener.Stop()
        Write-Host "Port $port is AVAILABLE" -ForegroundColor Green
        return $false
    } catch {
        Write-Host "Port $port is IN USE" -ForegroundColor Red
        return $true
    }
}

# Display network information
function Show-NetworkInfo {
    Write-Host "`nSystem Information:" -ForegroundColor Yellow
    $os = Get-WmiObject -Class Win32_OperatingSystem
    Write-Host "OS: $($os.Caption) $($os.Version)"
    Write-Host "Computer Name: $env:COMPUTERNAME"
    
    Write-Host "`nNetwork Interfaces:" -ForegroundColor Yellow
    Get-NetIPAddress | Where-Object { $_.AddressFamily -eq "IPv4" } | ForEach-Object {
        Write-Host "Interface: $($_.InterfaceAlias) - IP: $($_.IPAddress)"
    }
    
    Write-Host "`nChecking common Dash ports:" -ForegroundColor Yellow
    Test-PortInUse -port 8050
    Test-PortInUse -port 8080
}

# Attempt to kill processes using port 8050
function Stop-ProcessOnPort {
    param (
        [int]$port
    )
    
    Write-Host "`nAttempting to find processes using port $port..." -ForegroundColor Yellow
    $processList = netstat -ano | findstr :$port
    
    if ($processList) {
        Write-Host "Found processes using port $port:" -ForegroundColor Red
        Write-Host $processList
        
        # Extract PIDs
        $pids = @()
        $processList | ForEach-Object {
            if ($_ -match ":$port\s+.+?\s+.+?\s+(\d+)") {
                $pids += $matches[1]
            }
        }
        
        $pids = $pids | Select-Object -Unique
        
        if ($pids.Count -gt 0) {
            Write-Host "`nDo you want to kill these processes? (Y/N)" -ForegroundColor Yellow
            $response = Read-Host
            
            if ($response -eq "Y" -or $response -eq "y") {
                foreach ($pid in $pids) {
                    try {
                        $process = Get-Process -Id $pid
                        Write-Host "Killing process: $($process.Name) (PID: $pid)" -ForegroundColor Red
                        Stop-Process -Id $pid -Force
                        Write-Host "Process killed successfully" -ForegroundColor Green
                    } catch {
                        Write-Host "Failed to kill process with PID $pid : $_" -ForegroundColor Red
                    }
                }
                
                # Verify port is now available
                Start-Sleep -Seconds 1
                Test-PortInUse -port $port
            }
        }
    } else {
        Write-Host "No processes found using port $port" -ForegroundColor Green
    }
}

# Run network diagnostics Python script
function Run-PythonDiagnostics {
    Write-Host "`nRunning Python network diagnostics..." -ForegroundColor Yellow
    
    $pythonPath = "python"
    $scriptPath = "network_diagnostics.py"
    
    if (Test-Path $scriptPath) {
        try {
            & $pythonPath $scriptPath
            Write-Host "Python diagnostics completed successfully" -ForegroundColor Green
        } catch {
            Write-Host "Failed to run Python diagnostics: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Python diagnostics script not found at: $scriptPath" -ForegroundColor Red
    }
}

# Test simple app
function Test-SimpleApp {
    Write-Host "`nRunning simple test app..." -ForegroundColor Yellow
    
    $pythonPath = "python"
    $scriptPath = "app_network_test.py"
    
    if (Test-Path $scriptPath) {
        try {
            Write-Host "Starting simple test app. Press Ctrl+C to stop when finished testing." -ForegroundColor Cyan
            Write-Host "Try accessing the app at:" -ForegroundColor Cyan
            Write-Host "  http://localhost:8050" -ForegroundColor Cyan
            Write-Host "  http://127.0.0.1:8050" -ForegroundColor Cyan
            
            & $pythonPath $scriptPath
        } catch {
            Write-Host "Failed to run test app: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Test app script not found at: $scriptPath" -ForegroundColor Red
    }
}

# Fix original app
function Fix-OriginalApp {
    Write-Host "`nChecking original app file..." -ForegroundColor Yellow
    
    $appPath = "app.py"
    
    if (Test-Path $appPath) {
        $content = Get-Content $appPath -Raw
        
        if ($content -match "app\.run\(debug=True\)") {
            Write-Host "Found issue in app.py: Using app.run() instead of app.run_server()" -ForegroundColor Red
            Write-Host "Do you want to fix this issue? (Y/N)" -ForegroundColor Yellow
            $response = Read-Host
            
            if ($response -eq "Y" -or $response -eq "y") {
                $newContent = $content -replace "app\.run\(debug=True\)", "app.run_server(debug=True, host='0.0.0.0', port=8050)"
                $newContent | Set-Content $appPath
                Write-Host "Fixed app.py. The app should now be accessible in the browser." -ForegroundColor Green
            }
        } else {
            Write-Host "No obvious issues found in app.py" -ForegroundColor Green
        }
    } else {
        Write-Host "Original app file not found at: $appPath" -ForegroundColor Red
    }
}

# Main menu
function Show-Menu {
    Write-Host "`nPlease select an option:" -ForegroundColor Cyan
    Write-Host "1. Show network information" -ForegroundColor White
    Write-Host "2. Check and kill processes using port 8050" -ForegroundColor White
    Write-Host "3. Run Python network diagnostics" -ForegroundColor White
    Write-Host "4. Run simple test app" -ForegroundColor White
    Write-Host "5. Fix original app.py file" -ForegroundColor White
    Write-Host "6. Exit" -ForegroundColor White
    
    $choice = Read-Host "Enter your choice (1-6)"
    
    switch ($choice) {
        "1" { Show-NetworkInfo; Show-Menu }
        "2" { Stop-ProcessOnPort -port 8050; Show-Menu }
        "3" { Run-PythonDiagnostics; Show-Menu }
        "4" { Test-SimpleApp; Show-Menu }
        "5" { Fix-OriginalApp; Show-Menu }
        "6" { exit }
        default { Write-Host "Invalid choice, please try again" -ForegroundColor Red; Show-Menu }
    }
}

# Run the menu
Show-Menu
