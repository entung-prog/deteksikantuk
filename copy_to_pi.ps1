# PowerShell Script untuk Copy Files ke Raspberry Pi
# Usage: .\copy_to_pi.ps1 -PiIP "192.168.1.100"

param(
    [Parameter(Mandatory=$true)]
    [string]$PiIP,
    
    [Parameter(Mandatory=$false)]
    [string]$PiUser = "pi",
    
    [Parameter(Mandatory=$false)]
    [string]$TargetDir = "/home/pi/drowsiness-detection"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Copying files to Raspberry Pi: $PiIP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SCP is available
try {
    $scpVersion = scp -V 2>&1
    Write-Host "✓ SCP is available" -ForegroundColor Green
} catch {
    Write-Host "✗ SCP not found. Please install OpenSSH Client:" -ForegroundColor Red
    Write-Host "  Settings > Apps > Optional Features > Add OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

# Files to copy
$files = @(
    "backend_server.py",
    "drowsiness_test.html",
    "drowsiness_test.css",
    "drowsiness_test_hybrid.js",
    "requirements.txt",
    "deploy.sh",
    "README_DEPLOYMENT.md",
    "copy_to_pi.sh"
)

Write-Host "[1/3] Creating directory on Raspberry Pi..." -ForegroundColor Yellow
ssh "${PiUser}@${PiIP}" "mkdir -p ${TargetDir}"

Write-Host "[2/3] Copying application files..." -ForegroundColor Yellow
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  Copying $file..." -ForegroundColor Gray
        scp $file "${PiUser}@${PiIP}:${TargetDir}/"
    } else {
        Write-Host "  Warning: $file not found, skipping..." -ForegroundColor Yellow
    }
}

# Copy model file if exists
$modelPath = "..\best_model.h5"
if (Test-Path $modelPath) {
    Write-Host "[3/3] Copying model file..." -ForegroundColor Yellow
    scp $modelPath "${PiUser}@${PiIP}:${TargetDir}/"
} else {
    Write-Host "[3/3] Warning: best_model.h5 not found in parent directory, skipping..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Transfer Complete! ✅" -ForegroundColor Green
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
