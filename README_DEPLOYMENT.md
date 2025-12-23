# 🚀 Deployment Guide - Raspberry Pi

Panduan lengkap untuk deploy aplikasi Drowsiness Detection ke Raspberry Pi.

## 📋 Prerequisites

### Hardware
- Raspberry Pi 3/4/5 (recommended: Pi 4 dengan 4GB RAM)
- MicroSD card (minimal 16GB)
- Webcam USB atau Raspberry Pi Camera Module
- Power supply yang sesuai
- Koneksi internet

### Software
- Raspberry Pi OS (Bullseye atau lebih baru)
- SSH access ke Raspberry Pi (optional, untuk remote deployment)

## 🔧 Persiapan File

### 1. Copy File ke Raspberry Pi

**Opsi A: Menggunakan SCP (dari Windows)**

```powershell
# Copy seluruh folder webtest ke Raspberry Pi
scp -r c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest pi@<raspberry-pi-ip>:/home/pi/

# Copy file model (jika ada)
scp c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\best_model.h5 pi@<raspberry-pi-ip>:/home/pi/webtest/
```

**Opsi B: Menggunakan USB Drive**

1. Copy folder `webtest` ke USB drive
2. Colokkan USB ke Raspberry Pi
3. Mount dan copy file:
```bash
sudo mount /dev/sda1 /mnt
cp -r /mnt/webtest /home/pi/
```

**Opsi C: Clone dari Git (jika sudah di repository)**

```bash
cd /home/pi
git clone <your-repo-url> drowsiness-detection
cd drowsiness-detection
```

### 2. File yang Harus Ada di Raspberry Pi

Pastikan struktur folder seperti ini:

```
/home/pi/drowsiness-detection/
├── backend_server.py
├── drowsiness_test.html
├── drowsiness_test.css
├── drowsiness_test_hybrid.js
├── best_model.h5              # Model file
├── requirements.txt
├── deploy.sh
└── README_DEPLOYMENT.md
```

## 🚀 Deployment Steps

### Step 1: Login ke Raspberry Pi

```bash
ssh pi@<raspberry-pi-ip>
# Default password: raspberry (ganti setelah login pertama!)
```

### Step 2: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 3: Copy File Deployment

Jika belum copy file, lakukan sekarang (lihat bagian "Persiapan File" di atas).

### Step 4: Jalankan Deployment Script

```bash
cd /home/pi/drowsiness-detection
chmod +x deploy.sh
./deploy.sh
```

Script akan otomatis:
- ✅ Install dependencies sistem
- ✅ Buat Python virtual environment
- ✅ Install Python packages
- ✅ Setup systemd services
- ✅ Start aplikasi

### Step 5: Verifikasi

```bash
# Check service status
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-web

# Check logs
sudo journalctl -u drowsiness-backend -f
```

## 🌐 Akses Aplikasi

### Dari Raspberry Pi (Local)

```
http://localhost:8000/drowsiness_test.html
```

### Dari Device Lain di Network yang Sama

1. Cari IP Raspberry Pi:
```bash
hostname -I
```

2. Akses dari browser di device lain:
```
http://<raspberry-pi-ip>:8000/drowsiness_test.html
```

Contoh: `http://192.168.1.100:8000/drowsiness_test.html`

## 🔧 Management Commands

### Start/Stop Services

```bash
# Start
sudo systemctl start drowsiness-backend
sudo systemctl start drowsiness-web

# Stop
sudo systemctl stop drowsiness-backend
sudo systemctl stop drowsiness-web

# Restart
sudo systemctl restart drowsiness-backend
sudo systemctl restart drowsiness-web
```

### View Logs

```bash
# Backend logs (real-time)
sudo journalctl -u drowsiness-backend -f

# Web server logs (real-time)
sudo journalctl -u drowsiness-web -f

# Last 100 lines
sudo journalctl -u drowsiness-backend -n 100
```

### Enable/Disable Auto-start

```bash
# Enable (start on boot)
sudo systemctl enable drowsiness-backend
sudo systemctl enable drowsiness-web

# Disable
sudo systemctl disable drowsiness-backend
sudo systemctl disable drowsiness-web
```

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check logs
sudo journalctl -u drowsiness-backend -n 50

# Common issues:
# 1. Missing model file
ls -lh /home/pi/drowsiness-detection/best_model.h5

# 2. Port already in use
sudo lsof -i :5000

# 3. Permission issues
sudo chown -R pi:pi /home/pi/drowsiness-detection
```

### Low Performance / Slow FPS

Raspberry Pi memiliki keterbatasan hardware. Tips optimasi:

1. **Gunakan Raspberry Pi 4 (4GB RAM minimum)**
2. **Reduce model resolution** - edit `backend_server.py`:
```python
target_size = (96, 96)  # Reduce dari 224x224
```
3. **Enable GPU acceleration** (jika tersedia)
4. **Close unnecessary services**:
```bash
sudo systemctl stop bluetooth
sudo systemctl stop cups
```

### Webcam Not Detected

```bash
# List USB devices
lsusb

# Test webcam
v4l2-ctl --list-devices

# Install v4l-utils if not available
sudo apt-get install v4l-utils
```

### CORS Errors

Jika ada CORS error di browser:

1. Check backend logs
2. Pastikan Flask-CORS terinstall:
```bash
source /home/pi/drowsiness-detection/venv/bin/activate
pip install flask-cors
```

## 🔒 Security Tips

### 1. Change Default Password

```bash
passwd
```

### 2. Setup Firewall (Optional)

```bash
sudo apt-get install ufw
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # Backend
sudo ufw allow 8000  # Web
sudo ufw enable
```

### 3. Disable SSH Password Login (Use SSH Keys)

```bash
# Generate SSH key on your computer first
# Then copy to Pi:
ssh-copy-id pi@<raspberry-pi-ip>

# Edit SSH config
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

## 📊 Performance Monitoring

### Check System Resources

```bash
# CPU and Memory
htop

# Temperature
vcgencmd measure_temp

# Disk usage
df -h
```

### Monitor Service Performance

```bash
# Watch logs with timestamps
sudo journalctl -u drowsiness-backend -f --output=short-precise
```

## 🔄 Update Aplikasi

Jika ada perubahan code:

```bash
cd /home/pi/drowsiness-detection

# Backup current version
cp backend_server.py backend_server.py.backup

# Copy new files (via SCP atau Git pull)
# ...

# Restart services
sudo systemctl restart drowsiness-backend
sudo systemctl restart drowsiness-web
```

## 📱 Akses dari Internet (Advanced)

Jika ingin akses dari luar jaringan lokal:

### Opsi 1: Port Forwarding
- Setup port forwarding di router (port 8000 → Raspberry Pi IP)
- Gunakan Dynamic DNS (DuckDNS, No-IP)

### Opsi 2: Reverse Proxy (Recommended)
- Install Nginx
- Setup SSL dengan Let's Encrypt
- Gunakan Cloudflare Tunnel

### Opsi 3: VPN
- Setup WireGuard atau OpenVPN
- Akses Raspberry Pi via VPN

## 📞 Support

Jika ada masalah:

1. Check logs: `sudo journalctl -u drowsiness-backend -n 100`
2. Verify file permissions: `ls -la /home/pi/drowsiness-detection`
3. Test manual start:
```bash
cd /home/pi/drowsiness-detection
source venv/bin/activate
python backend_server.py
```

---

**Happy Deploying! 🎉**
