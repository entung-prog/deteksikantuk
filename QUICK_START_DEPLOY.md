# 🚀 Quick Start - Deployment ke Raspberry Pi

Panduan singkat untuk deploy aplikasi Drowsiness Detection ke Raspberry Pi.

## 📦 Isi Folder

```
webtest/
├── backend_server.py              # Flask backend server
├── drowsiness_test.html           # Web interface
├── drowsiness_test.css            # Styling
├── drowsiness_test_hybrid.js      # JavaScript logic
├── requirements.txt               # Python dependencies
├── deploy.sh                      # Deployment script (Linux/Mac)
├── copy_to_pi.sh                  # File transfer script (Linux/Mac)
├── copy_to_pi.ps1                 # File transfer script (Windows)
├── README_DEPLOYMENT.md           # Panduan lengkap
└── QUICK_START_DEPLOY.md          # File ini
```

## ⚡ Quick Deployment (3 Langkah)

### Dari Windows:

```powershell
# 1. Copy files ke Raspberry Pi
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
.\copy_to_pi.ps1 -PiIP "192.168.1.100"

# 2. SSH ke Raspberry Pi
ssh pi@192.168.1.100

# 3. Jalankan deployment
cd /home/pi/drowsiness-detection
chmod +x deploy.sh
./deploy.sh
```

### Dari Linux/Mac:

```bash
# 1. Copy files ke Raspberry Pi
cd /path/to/webtest
chmod +x copy_to_pi.sh
./copy_to_pi.sh 192.168.1.100

# 2. SSH ke Raspberry Pi
ssh pi@192.168.1.100

# 3. Jalankan deployment
cd /home/pi/drowsiness-detection
chmod +x deploy.sh
./deploy.sh
```

## 🌐 Akses Aplikasi

Setelah deployment selesai:

**Dari Raspberry Pi:**
```
http://localhost:8000/drowsiness_test.html
```

**Dari device lain di network yang sama:**
```
http://<raspberry-pi-ip>:8000/drowsiness_test.html
```

Contoh: `http://192.168.1.100:8000/drowsiness_test.html`

## 🔍 Cek Status

```bash
# Status services
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-web

# Lihat logs
sudo journalctl -u drowsiness-backend -f
```

## 🛠️ Management

```bash
# Restart services
sudo systemctl restart drowsiness-backend
sudo systemctl restart drowsiness-web

# Stop services
sudo systemctl stop drowsiness-backend
sudo systemctl stop drowsiness-web

# Start services
sudo systemctl start drowsiness-backend
sudo systemctl start drowsiness-web
```

## ⚠️ Troubleshooting

**Service tidak start:**
```bash
# Cek logs untuk error
sudo journalctl -u drowsiness-backend -n 50

# Cek file model ada
ls -lh /home/pi/drowsiness-detection/best_model.h5
```

**Webcam tidak terdeteksi:**
```bash
# List webcam
v4l2-ctl --list-devices

# Install v4l-utils jika perlu
sudo apt-get install v4l-utils
```

**Performance lambat:**
- Gunakan Raspberry Pi 4 (4GB RAM minimum)
- Close service yang tidak perlu
- Reduce model resolution di `backend_server.py`

## 📚 Dokumentasi Lengkap

Untuk panduan lengkap, troubleshooting detail, dan konfigurasi advanced, lihat:

**[README_DEPLOYMENT.md](README_DEPLOYMENT.md)**

## 📞 Quick Commands Reference

```bash
# Find Raspberry Pi IP
hostname -I

# Check system resources
htop

# Check temperature
vcgencmd measure_temp

# View all logs
sudo journalctl -u drowsiness-backend -u drowsiness-web -f
```

---

**Happy Deploying! 🎉**
