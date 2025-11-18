# Start All Services for AetherSegment AI CDP
# Windows PowerShell Script
# Run with: .\start_services.ps1

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AetherSegment AI - Starting All Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "OK Virtual environment found" -ForegroundColor Green
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "WARNING: Virtual environment not found at venv\" -ForegroundColor Yellow
    Write-Host "   Services will run using system Python" -ForegroundColor Yellow
}

Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found in project root!" -ForegroundColor Red
    Write-Host "   Please create a .env file with required configuration" -ForegroundColor Red
    Write-Host "   See env_template.txt for reference" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host "OK Configuration file found (project root .env)" -ForegroundColor Green

# Check if conversational segmentation .env exists
if (-not (Test-Path "conversational_segmentation\.env")) {
    Write-Host "WARNING: .env file not found in conversational_segmentation\" -ForegroundColor Yellow
    Write-Host "   Conversational segmentation may not work properly" -ForegroundColor Yellow
    Write-Host "   Please create conversational_segmentation\.env" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "OK Conversational segmentation .env found" -ForegroundColor Green
}

Write-Host ""

# Function to check if port is in use
function Test-Port {
    param($Port)
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    try {
        $listener.Start()
        $listener.Stop()
        return $false  # Port is available
    }
    catch {
        return $true   # Port is in use
    }
}

# Check if ports are available
$portsInUse = @()
if (Test-Port 5000) { $portsInUse += "5000 (Flask API)" }
if (Test-Port 8001) { $portsInUse += "8001 (Conversational Segmentation)" }
if (Test-Port 5500) { $portsInUse += "5500 (Frontend)" }

if ($portsInUse.Count -gt 0) {
    Write-Host "WARNING: Some ports are already in use:" -ForegroundColor Yellow
    foreach ($port in $portsInUse) {
        Write-Host "   - Port $port" -ForegroundColor Yellow
    }
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Check if required Python packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

$missingDeps = @()
try { python -c "import flask" 2>$null } catch { $missingDeps += "flask" }
try { python -c "import fastapi" 2>$null } catch { $missingDeps += "fastapi" }
try { python -c "import uvicorn" 2>$null } catch { $missingDeps += "uvicorn" }
try { python -c "import google.genai" 2>$null } catch { $missingDeps += "google-genai" }

if ($missingDeps.Count -gt 0) {
    Write-Host "WARNING: Some Python packages appear to be missing:" -ForegroundColor Yellow
    foreach ($dep in $missingDeps) {
        Write-Host "   - $dep" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "You may need to run: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
} else {
    Write-Host "OK Core dependencies found" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host ""

# Start Flask API (Port 5000) in new window
Write-Host "1. Starting Flask API (Port 5000)..." -ForegroundColor Yellow
$flaskCmd = "cd '$PWD'; if (Test-Path 'venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1 }; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  Flask API (Port 5000)' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; python run.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $flaskCmd
Start-Sleep -Seconds 2

# Start Conversational Segmentation Agent (Port 8001) in new window
Write-Host "2. Starting Conversational Segmentation Agent (Port 8001)..." -ForegroundColor Yellow
$segmentationCmd = "cd '$PWD'; if (Test-Path 'venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1 }; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  Conversational Segmentation Agent (Port 8001)' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; python run_segmentation.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $segmentationCmd
Start-Sleep -Seconds 2

# Start Frontend (Port 5500) in new window
Write-Host "3. Starting Frontend (Port 5500)..." -ForegroundColor Yellow
$frontendCmd = "cd '$PWD\frontend'; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '  Frontend Server (Port 5500)' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; python -m http.server 5500"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  All Services Started Successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor Cyan
Write-Host "  - Flask API:                    http://localhost:5000" -ForegroundColor White
Write-Host "  - Conversational Segmentation:  http://localhost:8001" -ForegroundColor White
Write-Host "  - Frontend:                     http://localhost:5500" -ForegroundColor White
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "  - Overview Dashboard:            http://localhost:5500/index.html" -ForegroundColor White
Write-Host "  - Campaign Segmentation:         http://localhost:5500/campaign-segmentation.html" -ForegroundColor White
Write-Host "  - Conversational Segmentation:   http://localhost:8001" -ForegroundColor White
Write-Host ""
Write-Host "To stop all services:" -ForegroundColor Yellow
Write-Host "  - Close each PowerShell window" -ForegroundColor White
Write-Host "  - Or use Ctrl+C in each window" -ForegroundColor White
Write-Host ""
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open browser to the application
Start-Process "http://localhost:5500/index.html"

Write-Host ""
Write-Host "OK Browser opened to application" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit this launcher window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
