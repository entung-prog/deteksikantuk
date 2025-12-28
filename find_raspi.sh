#!/bin/bash
# Script untuk mencari IP Raspberry Pi di network

echo "🔍 Mencari Raspberry Pi di network..."
echo ""

# Method 1: ARP (paling cepat)
echo "📡 Method 1: ARP Scan"
RASPI_MAC_PREFIXES="b8:27:eb|dc:a6:32|e4:5f:01"
ARP_RESULT=$(arp -a | grep -iE "$RASPI_MAC_PREFIXES")

if [ -n "$ARP_RESULT" ]; then
    echo "$ARP_RESULT"
    IP=$(echo "$ARP_RESULT" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)
else
    echo "❌ Tidak ditemukan via ARP"
fi
echo ""

# Method 2: Hostname
echo "📡 Method 2: Hostname Resolution"
if ping -c 1 -W 2 raspberrypi.local &>/dev/null; then
    HOSTNAME_IP=$(ping -c 1 raspberrypi.local | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)
    echo "✅ Found at raspberrypi.local ($HOSTNAME_IP)"
    IP=${IP:-$HOSTNAME_IP}
else
    echo "❌ Tidak ditemukan via hostname"
fi
echo ""

# Method 3: Nmap (jika tersedia)
if command -v nmap &> /dev/null; then
    echo "📡 Method 3: Nmap Scan (192.168.42.0/24)"
    NMAP_RESULT=$(nmap -sn 192.168.42.0/24 2>/dev/null | grep -B 2 -i "raspberry\|raspberrypi")
    if [ -n "$NMAP_RESULT" ]; then
        echo "$NMAP_RESULT"
        NMAP_IP=$(echo "$NMAP_RESULT" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)
        IP=${IP:-$NMAP_IP}
    else
        echo "❌ Tidak ditemukan via nmap"
    fi
    echo ""
fi

# Summary
echo "=========================================="
if [ -n "$IP" ]; then
    echo "✅ Raspberry Pi ditemukan!"
    echo ""
    echo "IP Address: $IP"
    echo ""
    echo "Akses Web Interface:"
    echo "  http://$IP:5000"
    echo ""
    echo "SSH Command:"
    echo "  ssh entung@$IP"
    echo ""
    echo "Quick Commands:"
    echo "  ssh entung@$IP                    # SSH login"
    echo "  scp file.txt entung@$IP:~/        # Copy file to Pi"
    echo "  xdg-open http://$IP:5000          # Open web UI (Linux)"
    echo "  open http://$IP:5000              # Open web UI (Mac)"
else
    echo "❌ Raspberry Pi tidak ditemukan"
    echo ""
    echo "Troubleshooting:"
    echo "1. Pastikan Pi sudah terhubung via USB tethering"
    echo "2. Tunggu 30-60 detik setelah koneksi"
    echo "3. Cek apakah tethering sudah enabled"
    echo "4. Coba: ping raspberrypi.local"
    echo "5. Cek interface: ip link show"
    echo ""
    echo "Manual check:"
    echo "  arp -a                           # Lihat semua devices"
    echo "  nmap -sn 192.168.42.0/24         # Scan subnet tethering"
    echo "  ping raspberrypi.local           # Ping hostname"
fi
echo "=========================================="
