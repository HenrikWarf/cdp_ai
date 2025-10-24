# PowerShell script to regenerate BigQuery data with recent timestamps
# Run this with: .\regenerate_data.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Regenerating AetherSegment AI Data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Regenerate data
Write-Host ""
Write-Host "Regenerating BigQuery data..." -ForegroundColor Yellow
Write-Host "(This will create fresh abandoned carts from the last 7 days)" -ForegroundColor Gray
Write-Host ""

python scripts\generate_data.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Data Regeneration Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Restart the backend: python run.py" -ForegroundColor White
    Write-Host "2. Open browser: http://localhost:8000" -ForegroundColor White
    Write-Host "3. Try your campaign analysis again" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Data generation failed!" -ForegroundColor Red
    Write-Host "Check the error message above." -ForegroundColor Yellow
    Write-Host ""
}

