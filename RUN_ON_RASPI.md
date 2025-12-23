# 🚀 Cara Menjalankan Project Langsung di Raspberry Pi

Panduan lengkap untuk menjalankan aplikasi Drowsiness Detection langsung di Raspberry Pi Anda.

---

## 📋 Yang Anda Butuhkan

- **Raspberry Pi** (Pi 3/4 recommended, minimal 2GB RAM)
- **Webcam USB** atau **Pi Camera Module**
- **SD Card** dengan Raspberry Pi OS sudah terinstall
- **Koneksi Internet** (untuk install dependencies)
- **File project** dari folder `webtest/`
- **File model** `best_model.h5` dari folder parent

---

## ⚡ Quick Start (3 Langkah)

### **Step 1: Copy Files ke Raspberry Pi**

**Dari Windows PowerShell:**

```powershell
# Ganti IP sesuai Raspberry Pi Anda
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
.\copy_to_pi.ps1 -PiIP "192.168.0.108"
```

**Atau manual dengan SCP:**

```powershell
# Buat directory
ssh entung@192.168.0.108 "mkdir -p ~/drowsiness-detection"

# Copy semua files
scp backend_server.py entung@192.168.0.108:~/drowsiness-detection/
scp drowsiness_test.html entung@192.168.0.108:~/drowsiness-detection/
scp drowsiness_test.css entung@192.168.0.108:~/drowsiness-detection/
scp drowsiness_test_hybrid.js entung@192.168.0.108:~/drowsiness-detection/
scp requirements.txt entung@192.168.0.108:~/drowsiness-detection/
scp ..\best_model.h5 entung@192.168.0.108:~/drowsiness-detection/
```

---

### **Step 2: SSH ke Raspberry Pi & Install Dependencies**

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Masuk ke folder project
cd ~/drowsiness-detection

# Update system
sudo apt-get update

# Install Python dependencies untuk OpenCV
sudo apt-get install -y python3-pip python3-venv
sudo apt-get install -y libopencv-dev python3-opencv
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev

# Buat virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages (TERMASUK flask-cors!)
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pillow==10.1.0

# Install TensorFlow Lite (lebih ringan untuk Raspberry Pi)
pip install tflite-runtime

# ATAU jika ingin full TensorFlow (lebih lambat tapi lebih kompatibel)
# pip install tensorflow==2.15.0
```

> [!IMPORTANT]
> **CORS sudah otomatis teratasi!** File `backend_server.py` sudah include `flask-cors`, jadi setelah install `flask-cors` di atas, masalah CORS akan hilang.

---

### **Step 3: Jalankan Aplikasi**

**Terminal 1 - Backend Server:**

```bash
cd ~/drowsiness-detection
source venv/bin/activate
python backend_server.py
```

Output yang benar:
```
Building model...
✅ Model loaded successfully!

============================================================
🚀 DROWSINESS DETECTION BACKEND SERVER
============================================================
Server running on: http://0.0.0.0:5001
API endpoints:
  - GET  /api/health  - Health check
  - POST /api/predict - Predict drowsiness
============================================================
```

**Terminal 2 - Web Server (buka SSH baru):**

```bash
cd ~/drowsiness-detection
python3 -m http.server 8000
```

---

## 🌐 Akses Aplikasi

### **Dari Raspberry Pi sendiri:**
```
http://localhost:8000/drowsiness_test.html
```

### **Dari komputer/laptop di network yang sama:**
```
http://192.168.0.108:8000/drowsiness_test.html
```
*(Ganti `192.168.0.108` dengan IP Raspberry Pi Anda)*

### **Cek IP Raspberry Pi:**
```bash
hostname -I
```

---

## 🔧 Troubleshooting

### ❌ **Masalah: CORS Error**

**Penyebab:** `flask-cors` belum terinstall

**Solusi:**
```bash
source venv/bin/activate
pip install flask-cors==4.0.0
# Restart backend server
```

---

### ❌ **Masalah: ModuleNotFoundError: No module named 'flask'**

**Penyebab:** Virtual environment tidak aktif atau packages belum terinstall

**Solusi:**
```bash
cd ~/drowsiness-detection
source venv/bin/activate
pip install -r requirements.txt
```

---

### ❌ **Masalah: Webcam tidak terdeteksi**

**Cek webcam:**
```bash
# List semua video devices
ls -l /dev/video*

# Install v4l-utils
sudo apt-get install v4l-utils

# List webcam details
v4l2-ctl --list-devices
```

**Test webcam dengan Python:**
```python
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ Webcam OK!")
else:
    print("❌ Webcam tidak terdeteksi")
cap.release()
```

---

### ❌ **Masalah: Model loading error**

**Cek file model ada:**
```bash
ls -lh ~/drowsiness-detection/best_model.h5
```

**Jika file tidak ada, copy lagi:**
```powershell
# Dari Windows
scp ..\best_model.h5 entung@192.168.0.108:~/drowsiness-detection/
```

---

### ❌ **Masalah: Performance lambat / lag**

**Solusi:**

1. **Gunakan TensorFlow Lite** (lebih ringan):
```bash
pip uninstall tensorflow
pip install tflite-runtime
```

2. **Reduce FPS di browser:**
   - Buka `drowsiness_test_hybrid.js`
   - Cari `setInterval` atau FPS setting
   - Turunkan dari 30 FPS ke 10-15 FPS

3. **Close aplikasi lain:**
```bash
# Cek memory usage
free -h

# Cek CPU usage
htop
```

4. **Overclock Raspberry Pi** (optional, hati-hati!):
```bash
sudo nano /boot/config.txt
# Tambahkan:
# over_voltage=2
# arm_freq=1750
```

---

## 🔄 Auto-Start on Boot (Optional)

Jika ingin aplikasi otomatis jalan saat Raspberry Pi boot:

### **1. Create systemd service untuk Backend**

```bash
sudo nano /etc/systemd/system/drowsiness-backend.service
```

Isi dengan:
```ini
[Unit]
Description=Drowsiness Detection Backend
After=network.target

[Service]
Type=simple
User=entung
WorkingDirectory=/home/entung/drowsiness-detection
Environment="PATH=/home/entung/drowsiness-detection/venv/bin"
ExecStart=/home/entung/drowsiness-detection/venv/bin/python backend_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### **2. Create systemd service untuk Web Server**

```bash
sudo nano /etc/systemd/system/drowsiness-web.service
```

Isi dengan:
```ini
[Unit]
Description=Drowsiness Detection Web Server
After=network.target

[Service]
Type=simple
User=entung
WorkingDirectory=/home/entung/drowsiness-detection
ExecStart=/usr/bin/python3 -m http.server 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### **3. Enable & Start Services**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (auto-start on boot)
sudo systemctl enable drowsiness-backend
sudo systemctl enable drowsiness-web

# Start services now
sudo systemctl start drowsiness-backend
sudo systemctl start drowsiness-web

# Check status
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-web
```

### **4. Management Commands**

```bash
# Restart services
sudo systemctl restart drowsiness-backend
sudo systemctl restart drowsiness-web

# Stop services
sudo systemctl stop drowsiness-backend
sudo systemctl stop drowsiness-web

# View logs
sudo journalctl -u drowsiness-backend -f
sudo journalctl -u drowsiness-web -f
```

---

## 📊 Monitoring

### **Cek Resource Usage:**

```bash
# CPU & Memory
htop

# Temperature
vcgencmd measure_temp

# Disk space
df -h
```

### **Cek Logs:**

```bash
# Backend logs (jika pakai systemd)
sudo journalctl -u drowsiness-backend -n 50

# Web server logs
sudo journalctl -u drowsiness-web -n 50
```

---

## 🎯 Summary

| Component | Port | Command |
|-----------|------|---------|
| **Backend** | 5001 | `python backend_server.py` |
| **Web Server** | 8000 | `python3 -m http.server 8000` |
| **Access URL** | - | `http://<raspi-ip>:8000/drowsiness_test.html` |

---

## ✅ Checklist

- [ ] Files sudah di-copy ke Raspberry Pi
- [ ] Virtual environment sudah dibuat
- [ ] Dependencies sudah terinstall (termasuk `flask-cors`)
- [ ] Backend server berjalan di port 5001
- [ ] Web server berjalan di port 8000
- [ ] Bisa akses dari browser
- [ ] Webcam terdeteksi
- [ ] Model loading berhasil
- [ ] **CORS error sudah hilang!**

---

## 🆘 Butuh Bantuan?

**Cek status lengkap:**
```bash
# Cek semua service
systemctl status drowsiness-*

# Cek network
ip addr show

# Cek webcam
v4l2-ctl --list-devices

# Test backend API
curl http://localhost:5001/api/health
```

**Expected response:**
```json
{"model_loaded":true,"status":"ok"}
```

---

**Happy Coding! 🎉**
