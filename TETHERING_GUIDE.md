# Cara Cek IP Raspberry Pi via Tethering

## Metode 1: ARP Scan (Paling Mudah) ✅

### Di Linux/Mac:
```bash
# Scan semua device di network
arp -a

# Atau lebih spesifik
arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01"  # Raspberry Pi MAC prefix
```

### Di Windows:
```cmd
# Command Prompt
arp -a

# PowerShell
Get-NetNeighbor -AddressFamily IPv4
```

**Output contoh:**
```
? (192.168.42.129) at b8:27:eb:xx:xx:xx [ether] on usb0
```
IP Raspberry Pi: `192.168.42.129`

---

## Metode 2: Nmap Scan

### Install nmap (jika belum ada):
```bash
# Ubuntu/Debian
sudo apt install nmap

# Mac
brew install nmap

# Windows
# Download dari https://nmap.org/download.html
```

### Scan network:
```bash
# Scan subnet tethering (biasanya 192.168.42.x atau 192.168.43.x)
nmap -sn 192.168.42.0/24

# Atau scan dengan hostname
nmap -sn 192.168.42.0/24 | grep -B 2 "raspberrypi"
```

**Output:**
```
Nmap scan report for raspberrypi.local (192.168.42.129)
Host is up (0.0012s latency).
```

---

## Metode 3: Hostname Resolution

### mDNS (Avahi/Bonjour):
```bash
# Ping hostname
ping raspberrypi.local

# Resolve IP
avahi-resolve -n raspberrypi.local

# Atau
getent hosts raspberrypi.local
```

**Output:**
```
raspberrypi.local       192.168.42.129
```

---

## Metode 4: Check DHCP Leases

### Di Linux (laptop sebagai DHCP server):
```bash
# Check dnsmasq leases
cat /var/lib/misc/dnsmasq.leases

# Atau NetworkManager
nmcli device show usb0 | grep IP4
```

### Di Android (jika tethering dari HP):
- Buka Settings → Hotspot & Tethering
- Lihat "Connected devices"
- Akan muncul "raspberrypi" dengan IP-nya

---

## Metode 5: Script Otomatis

Buat script untuk auto-detect:

```bash
#!/bin/bash
# find_raspi.sh

echo "🔍 Mencari Raspberry Pi di network..."
echo ""

# Method 1: ARP
echo "Method 1: ARP Scan"
arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01" || echo "Not found via ARP"
echo ""

# Method 2: Hostname
echo "Method 2: Hostname Resolution"
ping -c 1 raspberrypi.local 2>/dev/null && echo "✅ Found at raspberrypi.local" || echo "Not found via hostname"
echo ""

# Method 3: Nmap (if installed)
if command -v nmap &> /dev/null; then
    echo "Method 3: Nmap Scan"
    nmap -sn 192.168.42.0/24 | grep -B 2 "Raspberry\|raspberrypi" || echo "Not found via nmap"
else
    echo "Method 3: Nmap not installed (skip)"
fi
echo ""

# Try to get IP
IP=$(arp -a | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)

if [ -n "$IP" ]; then
    echo "✅ Raspberry Pi found at: $IP"
    echo ""
    echo "Access web interface:"
    echo "  http://$IP:5000"
    echo ""
    echo "SSH command:"
    echo "  ssh entung@$IP"
else
    echo "❌ Raspberry Pi not found"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure Pi is connected via USB tethering"
    echo "2. Wait 30 seconds after connecting"
    echo "3. Check if tethering is enabled on phone/laptop"
    echo "4. Try: ping raspberrypi.local"
fi
```

**Usage:**
```bash
chmod +x find_raspi.sh
./find_raspi.sh
```

---

## Quick Reference

### Tethering IP Ranges

| Tethering Type | IP Range | Interface |
|----------------|----------|-----------|
| **USB Tethering (Android)** | 192.168.42.x | usb0 |
| **USB Tethering (iPhone)** | 172.20.10.x | eth1 |
| **WiFi Hotspot** | 192.168.43.x | wlan0 |
| **Bluetooth** | 192.168.44.x | bnep0 |

### Common Commands

```bash
# Quick check
arp -a | grep 192.168.42

# Scan subnet
nmap -sn 192.168.42.0/24

# Ping hostname
ping raspberrypi.local

# SSH
ssh entung@raspberrypi.local
# atau
ssh entung@192.168.42.129

# Access web
http://raspberrypi.local:5000
# atau
http://192.168.42.129:5000
```

---

## Troubleshooting

### Pi tidak terdeteksi?

1. **Check koneksi USB**
   ```bash
   # Di laptop, check USB devices
   lsusb | grep -i "raspberry\|broadcom"
   ```

2. **Check network interface**
   ```bash
   # List interfaces
   ip link show
   # atau
   ifconfig
   
   # Should see usb0 or similar
   ```

3. **Restart network**
   ```bash
   # Di Pi (via keyboard/monitor)
   sudo systemctl restart networking
   
   # Atau reboot
   sudo reboot
   ```

4. **Check tethering settings**
   - Pastikan USB tethering enabled di HP/laptop
   - Coba disconnect & reconnect
   - Tunggu 30 detik setelah connect

5. **Manual IP check di Pi**
   ```bash
   # Di Pi (via keyboard/monitor atau SSH lain)
   hostname -I
   # atau
   ip addr show
   ```

---

## Pro Tips

### 1. Set Static IP di Pi

Edit `/etc/dhcpcd.conf`:
```bash
interface usb0
static ip_address=192.168.42.100/24
```

Sekarang Pi selalu dapat IP `192.168.42.100` saat tethering.

### 2. Add to /etc/hosts

Di laptop, tambahkan:
```bash
sudo nano /etc/hosts
```

```
192.168.42.129  raspi
```

Sekarang bisa akses dengan:
```bash
ssh entung@raspi
http://raspi:5000
```

### 3. Create Alias

Di `~/.bashrc` atau `~/.zshrc`:
```bash
alias raspi-ssh='ssh entung@raspberrypi.local'
alias raspi-web='xdg-open http://raspberrypi.local:5000'
alias raspi-ip='arp -a | grep -i "b8:27:eb\|dc:a6:32" | grep -oE "([0-9]{1,3}\.){3}[0-9]{1,3}"'
```

Usage:
```bash
raspi-ssh    # SSH to Pi
raspi-web    # Open web UI
raspi-ip     # Show Pi IP
```

---

## Status: ✅ Ready for Tethering!

Gunakan salah satu metode di atas untuk cek IP Raspberry Pi saat tethering.
