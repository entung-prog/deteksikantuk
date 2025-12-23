# PowerShell script to scan for Raspberry Pi on network
# Scans common IP ranges and tests SSH connectivity

param(
    [Parameter(Mandatory=$false)]
    [string]$NetworkPrefix = "192.168.0"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Scanning for Raspberry Pi on network..." -ForegroundColor Cyan
Write-Host "Network: $NetworkPrefix.x" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$found = @()

# Scan range 1-254
Write-Host "Scanning IP range $NetworkPrefix.1 to $NetworkPrefix.254..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le 254; $i++) {
    $ip = "$NetworkPrefix.$i"
    
    # Skip known IPs
    if ($ip -eq "$NetworkPrefix.101") { continue }  # Your PC
    if ($ip -eq "$NetworkPrefix.1") { continue }    # Gateway
    if ($ip -eq "$NetworkPrefix.255") { continue }  # Broadcast
    
    # Quick ping test (timeout 100ms)
    $ping = Test-Connection -ComputerName $ip -Count 1 -Quiet -TimeoutSeconds 1
    
    if ($ping) {
        Write-Host "[FOUND] $ip is alive" -ForegroundColor Green
        
        # Try SSH connection test (port 22)
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        try {
            $tcpClient.ConnectAsync($ip, 22).Wait(1000) | Out-Null
            if ($tcpClient.Connected) {
                Write-Host "  -> SSH port (22) is OPEN" -ForegroundColor Green
                $found += $ip
            } else {
                Write-Host "  -> SSH port (22) is closed" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  -> SSH port (22) is closed" -ForegroundColor Yellow
        } finally {
            $tcpClient.Close()
        }
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Scan Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($found.Count -gt 0) {
    Write-Host "Found $($found.Count) device(s) with SSH enabled:" -ForegroundColor Green
    foreach ($ip in $found) {
        Write-Host "  - $ip" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Try connecting with:" -ForegroundColor Cyan
    Write-Host "  ssh pi@$($found[0])" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Or run deployment with:" -ForegroundColor Cyan
    Write-Host "  .\deploy_simple.ps1 -PiIP `"$($found[0])`"" -ForegroundColor Gray
} else {
    Write-Host "No devices with SSH found on network $NetworkPrefix.x" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible reasons:" -ForegroundColor Yellow
    Write-Host "  1. Raspberry Pi is not powered on" -ForegroundColor Gray
    Write-Host "  2. Raspberry Pi is not connected to network" -ForegroundColor Gray
    Write-Host "  3. SSH is not enabled on Raspberry Pi" -ForegroundColor Gray
    Write-Host "  4. Raspberry Pi is on a different network" -ForegroundColor Gray
}

Write-Host ""
