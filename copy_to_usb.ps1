# PowerShell Script - Copy Files to USB for Raspberry Pi Deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$UsbDrive
)

$sourceDir = "c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest"
$modelFile = "c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\best_model.h5"
$targetDir = "$UsbDrive\drowsiness"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Copying files to USB: $UsbDrive" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Create target directory
Write-Host "[1/3] Creating directory on USB..." -ForegroundColor Yellow
New-Item -Path $targetDir -ItemType Directory -Force | Out-Null

# Copy application files
Write-Host "[2/3] Copying application files..." -ForegroundColor Yellow
$files = @(
    "backend_server.py",
    "drowsiness_test.html",
    "drowsiness_test.css",
    "drowsiness_test_hybrid.js",
    "requirements.txt",
    "deploy_manual.sh"
)

foreach ($file in $files) {
    $sourcePath = Join-Path $sourceDir $file
    if (Test-Path $sourcePath) {
        Write-Host "  Copying $file..." -ForegroundColor Gray
        Copy-Item $sourcePath -Destination $targetDir -Force
    } else {
        Write-Host "  Warning: $file not found" -ForegroundColor Yellow
    }
}

# Copy model file
Write-Host "[3/3] Copying model file..." -ForegroundColor Yellow
if (Test-Path $modelFile) {
    Copy-Item $modelFile -Destination $targetDir -Force
    Write-Host "  Copied best_model.h5" -ForegroundColor Gray
} else {
    Write-Host "  Warning: best_model.h5 not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Files copied to USB successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Eject USB safely from Windows" -ForegroundColor White
Write-Host "2. Plug USB into Raspberry Pi" -ForegroundColor White
Write-Host "3. On Raspberry Pi, run:" -ForegroundColor White
Write-Host ""
Write-Host "   cp -r /media/pi/*/drowsiness /home/pi/drowsiness-detection" -ForegroundColor Gray
Write-Host "   cd /home/pi/drowsiness-detection" -ForegroundColor Gray
Write-Host "   chmod +x deploy_manual.sh" -ForegroundColor Gray
Write-Host "   ./deploy_manual.sh" -ForegroundColor Gray
Write-Host ""
