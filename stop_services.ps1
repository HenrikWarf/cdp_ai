# Stop All Services for AetherSegment AI CDP
# Windows PowerShell Script
# Run with: .\stop_services.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AetherSegment AI - Stopping All Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Finding and stopping services..." -ForegroundColor Yellow
Write-Host ""

$stopped = 0

# Function to get process by port
function Get-ProcessByPort {
    param($Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            return Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        }
    }
    catch {
        return $null
    }
    return $null
}

# Stop Flask API (Port 5000)
Write-Host "Checking Flask API (Port 5000)..." -ForegroundColor Yellow
$process = Get-ProcessByPort 5000
if ($process) {
    Write-Host "  Stopping $($process.ProcessName) (PID: $($process.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force
    Write-Host "  OK Flask API stopped" -ForegroundColor Green
    $stopped++
} else {
    Write-Host "  No service running on port 5000" -ForegroundColor Gray
}

# Stop Conversational Segmentation Agent (Port 8001)
Write-Host "Checking Conversational Segmentation Agent (Port 8001)..." -ForegroundColor Yellow
$process = Get-ProcessByPort 8001
if ($process) {
    Write-Host "  Stopping $($process.ProcessName) (PID: $($process.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force
    Write-Host "  OK Conversational Segmentation Agent stopped" -ForegroundColor Green
    $stopped++
} else {
    Write-Host "  No service running on port 8001" -ForegroundColor Gray
}

# Stop Frontend (Port 5500)
Write-Host "Checking Frontend (Port 5500)..." -ForegroundColor Yellow
$process = Get-ProcessByPort 5500
if ($process) {
    Write-Host "  Stopping $($process.ProcessName) (PID: $($process.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force
    Write-Host "  OK Frontend stopped" -ForegroundColor Green
    $stopped++
} else {
    Write-Host "  No service running on port 5500" -ForegroundColor Gray
}

Write-Host ""

# Check for any remaining Python processes related to our services
Write-Host "Checking for orphaned Python processes..." -ForegroundColor Yellow
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*run.py*" -or 
    $_.CommandLine -like "*run_segmentation.py*" -or
    $_.CommandLine -like "*http.server*"
}

if ($pythonProcesses) {
    Write-Host "  Found $($pythonProcesses.Count) orphaned process(es)" -ForegroundColor Yellow
    $cleanup = Read-Host "  Stop these processes too? (y/n)"
    if ($cleanup -eq "y") {
        foreach ($proc in $pythonProcesses) {
            try {
                Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                Write-Host "  OK Stopped orphaned process (PID: $($proc.Id))" -ForegroundColor Green
                $stopped++
            } catch {
                Write-Host "  WARNING: Could not stop process (PID: $($proc.Id))" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "  No orphaned processes found" -ForegroundColor Green
}

Write-Host ""

if ($stopped -gt 0) {
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  $stopped service(s) stopped successfully" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
} else {
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "  No services were running" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
}

Write-Host ""

# Ask about closing PowerShell windows
Write-Host "Note: Service windows may still be open." -ForegroundColor Yellow
Write-Host "You can close them manually if needed." -ForegroundColor Yellow
Write-Host ""

# Clean up log files (optional)
$clearLogs = Read-Host "Do you want to clear log files in logs/? (y/n)"
if ($clearLogs -eq "y") {
    if (Test-Path "logs") {
        Remove-Item "logs\*.log" -Force -ErrorAction SilentlyContinue
        Write-Host "OK Log files cleared" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
