# PowerShell Script - Test SSH Connection to Raspberry Pi

param(
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.0.108",
    
    [Parameter(Mandatory=$false)]
    [string]$PiUser = "pi"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Testing SSH Connection to Raspberry Pi" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Target: $PiUser@$PiIP" -ForegroundColor White
Write-Host ""

# Test 1: Ping
Write-Host "[1/4] Testing network connectivity (ping)..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $PiIP -Count 2 -Quiet

if ($pingResult) {
    Write-Host "  ✓ Ping successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ Ping failed - Raspberry Pi not reachable" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  - Raspberry Pi is not powered on" -ForegroundColor Gray
    Write-Host "  - Wrong IP address" -ForegroundColor Gray
    Write-Host "  - Not on same network" -ForegroundColor Gray
    exit 1
}

# Test 2: SSH Port
Write-Host ""
Write-Host "[2/4] Testing SSH port (22)..." -ForegroundColor Yellow
$portTest = Test-NetConnection -ComputerName $PiIP -Port 22 -WarningAction SilentlyContinue

if ($portTest.TcpTestSucceeded) {
    Write-Host "  ✓ SSH port is open" -ForegroundColor Green
} else {
    Write-Host "  ✗ SSH port is closed or filtered" -ForegroundColor Red
    Write-Host ""
    Write-Host "SSH is not enabled on Raspberry Pi" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable SSH:" -ForegroundColor Cyan
    Write-Host "  1. Login to Raspberry Pi (monitor + keyboard)" -ForegroundColor Gray
    Write-Host "  2. Run: sudo raspi-config" -ForegroundColor Gray
    Write-Host "  3. Interface Options > SSH > Enable" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Or create 'ssh' file in boot partition" -ForegroundColor Cyan
    exit 1
}

# Test 3: SSH Connection
Write-Host ""
Write-Host "[3/4] Testing SSH connection..." -ForegroundColor Yellow
Write-Host "  Attempting to connect (this may take a few seconds)..." -ForegroundColor Gray

$sshTest = ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$PiUser@$PiIP" "echo 'SSH OK'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ SSH connection successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ SSH connection failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $sshTest" -ForegroundColor Yellow
    
    if ($sshTest -match "Permission denied") {
        Write-Host ""
        Write-Host "Authentication failed - check username/password" -ForegroundColor Yellow
    } elseif ($sshTest -match "Connection refused") {
        Write-Host ""
        Write-Host "SSH service not running on Raspberry Pi" -ForegroundColor Yellow
    }
    exit 1
}

# Test 4: Get System Info
Write-Host ""
Write-Host "[4/4] Getting Raspberry Pi information..." -ForegroundColor Yellow
$hostname = ssh -o ConnectTimeout=5 "$PiUser@$PiIP" "hostname" 2>&1
$osVersion = ssh -o ConnectTimeout=5 "$PiUser@$PiIP" "cat /etc/os-release | grep PRETTY_NAME" 2>&1
$uptime = ssh -o ConnectTimeout=5 "$PiUser@$PiIP" "uptime -p" 2>&1

Write-Host "  Hostname: $hostname" -ForegroundColor Gray
Write-Host "  OS: $($osVersion -replace 'PRETTY_NAME=', '' -replace '\"', '')" -ForegroundColor Gray
Write-Host "  Uptime: $uptime" -ForegroundColor Gray

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "SSH Connection Test: PASSED ✅" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now deploy using:" -ForegroundColor Cyan
Write-Host "  .\deploy_simple.ps1 -PiIP `"$PiIP`"" -ForegroundColor Gray
Write-Host ""
Write-Host "Or connect manually:" -ForegroundColor Cyan
Write-Host "  ssh $PiUser@$PiIP" -ForegroundColor Gray
Write-Host ""
