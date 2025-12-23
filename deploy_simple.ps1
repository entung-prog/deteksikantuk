# Simple PowerShell Script untuk Copy Files ke Raspberry Pi
# Usage: .\deploy_simple.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.0.108",
    
    [Parameter(Mandatory=$false)]
    [string]$PiUser = "pi",
    
    [Parameter(Mandatory=$false)]
    [string]$TargetDir = "/home/pi/drowsiness-detection"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Copying files to Raspberry Pi: $PiIP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Files to copy
$files = @(
    "backend_server.py",
    "drowsiness_test.html",
    "drowsiness_test.css",
    "drowsiness_test_hybrid.js",
    "requirements.txt",
    "deploy.sh",
    "README_DEPLOYMENT.md"
)

Write-Host "[1/3] Creating directory on Raspberry Pi..." -ForegroundColor Yellow
ssh "${PiUser}@${PiIP}" "mkdir -p ${TargetDir}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot connect to Raspberry Pi. Please check:" -ForegroundColor Red
    Write-Host "  1. IP address is correct: $PiIP" -ForegroundColor Yellow
    Write-Host "  2. Raspberry Pi is powered on and connected to network" -ForegroundColor Yellow
    Write-Host "  3. SSH is enabled on Raspberry Pi" -ForegroundColor Yellow
    exit 1
}

Write-Host "[2/3] Copying application files..." -ForegroundColor Yellow
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  Copying $file..." -ForegroundColor Gray
        scp $file "${PiUser}@${PiIP}:${TargetDir}/"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Error copying $file" -ForegroundColor Red
        }
    } else {
        Write-Host "  Warning: $file not found, skipping..." -ForegroundColor Yellow
    }
}

# Copy model file if exists
$modelPath = "..\best_model.h5"
if (Test-Path $modelPath) {
    Write-Host "[3/3] Copying model file..." -ForegroundColor Yellow
    scp $modelPath "${PiUser}@${PiIP}:${TargetDir}/"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Error copying model file" -ForegroundColor Red
    }
} else {
    Write-Host "[3/3] Warning: best_model.h5 not found in parent directory" -ForegroundColor Yellow
    Write-Host "  Looking for: $((Resolve-Path $modelPath -ErrorAction SilentlyContinue).Path)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Transfer Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. SSH to Raspberry Pi:" -ForegroundColor White
Write-Host "   ssh ${PiUser}@${PiIP}" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run deployment script:" -ForegroundColor White
Write-Host "   cd ${TargetDir}" -ForegroundColor Gray
Write-Host "   chmod +x deploy.sh" -ForegroundColor Gray
Write-Host "   ./deploy.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "Or run this command to do it automatically:" -ForegroundColor Cyan
Write-Host "   ssh ${PiUser}@${PiIP} 'cd ${TargetDir} && chmod +x deploy.sh && ./deploy.sh'" -ForegroundColor Gray
Write-Host ""
