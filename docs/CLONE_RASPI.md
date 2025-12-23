# 🚀 Cara Clone Repository di Raspberry Pi

Panduan lengkap untuk clone project dari GitHub ke Raspberry Pi dan menjalankannya.

---

## 📋 Prerequisites

- Raspberry Pi sudah terinstall Raspberry Pi OS
- Koneksi internet aktif
- Git sudah terinstall (biasanya sudah default)

---

## ⚡ Quick Start (Clone & Run)

### **Step 1: SSH ke Raspberry Pi**

```bash
# Dari Windows PowerShell
ssh entung@192.168.0.108
```

---

### **Step 2: Install Git (jika belum ada)**

```bash
# Cek apakah git sudah terinstall
git --version

# Jika belum, install git
sudo apt-get update
sudo apt-get install -y git
```

---

### **Step 3: Clone Repository**

```bash
# Clone dari GitHub
git clone https://github.com/entung-prog/deteksikantuk.git

# Masuk ke folder project
cd deteksikantuk
```

> [!TIP]
> **Jika repository private**, Anda perlu authenticate:
> ```bash
> # Gunakan Personal Access Token (PAT)
> git clone https://YOUR_TOKEN@github.com/entung-prog/deteksikantuk.git
> ```
> 
> **Cara buat PAT:**
> 1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
> 2. Generate new token → Pilih scope `repo`
> 3. Copy token dan gunakan di command di atas

---

### **Step 4: Cek Isi Repository**

```bash
# Lihat struktur folder
ls -la

# Pastikan file-file penting ada
ls -l best_model.h5
ls -l backend_server.py
ls -l drowsiness_test.html
```

---

### **Step 5: Install Dependencies**

```bash
# Update system
sudo apt-get update

# Install system dependencies untuk OpenCV
sudo apt-get install -y python3-pip python3-venv
sudo apt-get install -y libopencv-dev python3-opencv
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev

# Buat virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pillow==10.1.0

# Install TensorFlow (pilih salah satu)
# Option 1: TensorFlow Lite (lebih ringan, recommended)
pip install tflite-runtime

# Option 2: Full TensorFlow (lebih lambat tapi lebih kompatibel)
# pip install tensorflow==2.15.0
```

> [!IMPORTANT]
> **CORS sudah otomatis teratasi!** Setelah install `flask-cors`, masalah CORS akan hilang.

---

### **Step 6: Jalankan Aplikasi**

**Terminal 1 - Backend Server:**

```bash
cd ~/deteksikantuk
source venv/bin/activate
python backend_server.py
```

**Output yang benar:**
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
cd ~/deteksikantuk
python3 -m http.server 8000
```

---

## 🌐 Akses Aplikasi

### **Dari Raspberry Pi:**
```
http://localhost:8000/drowsiness_test.html
```

### **Dari komputer/laptop di network yang sama:**
```
http://192.168.0.108:8000/drowsiness_test.html
```
*(Ganti IP sesuai Raspberry Pi Anda)*

### **Cek IP Raspberry Pi:**
```bash
hostname -I
```

---

## 🔄 Update Repository (Pull Changes)

Jika ada perubahan di GitHub dan ingin update di Raspberry Pi:

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Masuk ke folder project
cd ~/deteksikantuk

# Pull perubahan terbaru
git pull origin main

# Restart services jika perlu
sudo systemctl restart drowsiness-backend
sudo systemctl restart drowsiness-web
```

---

## 🔧 Troubleshooting

### ❌ **Error: Permission denied (publickey)**

**Solusi 1 - Gunakan HTTPS (recommended):**
```bash
git clone https://github.com/entung-prog/deteksikantuk.git
```

**Solusi 2 - Setup SSH Key:**
```bash
# Generate SSH key di Raspberry Pi
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Tekan Enter untuk semua pertanyaan

# Copy public key
cat ~/.ssh/id_rsa.pub

# Paste ke GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key
# Paste isi dari id_rsa.pub

# Clone dengan SSH
git clone git@github.com:entung-prog/deteksikantuk.git
```

---

### ❌ **Error: fatal: could not create work tree dir**

**Penyebab:** Permission issue

**Solusi:**
```bash
# Clone di home directory
cd ~
git clone https://github.com/entung-prog/deteksikantuk.git
```

---

### ❌ **Error: Model file not found**

**Cek file model:**
```bash
ls -lh ~/deteksikantuk/best_model.h5
```

**Jika tidak ada, pastikan file ada di repository GitHub:**
1. Cek di GitHub apakah `best_model.h5` sudah di-push
2. Jika belum, push dari Windows:
   ```powershell
   cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline
   git add best_model.h5
   git commit -m "Add model file"
   git push origin main
   ```
3. Pull lagi di Raspberry Pi:
   ```bash
   cd ~/deteksikantuk
   git pull origin main
   ```

> [!WARNING]
> **File besar (>100MB) tidak bisa di-push ke GitHub biasa!**
> 
> Jika `best_model.h5` lebih dari 100MB, gunakan salah satu cara:
> 
> **Option 1: Git LFS (Large File Storage)**
> ```bash
> # Di Windows
> git lfs install
> git lfs track "*.h5"
> git add .gitattributes
> git add best_model.h5
> git commit -m "Add model with LFS"
> git push origin main
> ```
> 
> **Option 2: Copy manual dengan SCP**
> ```powershell
> # Dari Windows
> scp best_model.h5 entung@192.168.0.108:~/deteksikantuk/
> ```
> 
> **Option 3: Upload ke cloud (Google Drive, Dropbox) dan download di Raspi**
> ```bash
> # Di Raspberry Pi
> cd ~/deteksikantuk
> wget "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID" -O best_model.h5
> ```

---

### ❌ **CORS Error**

**Solusi:**
```bash
source venv/bin/activate
pip install flask-cors==4.0.0
# Restart backend
```

---

### ❌ **Webcam tidak terdeteksi**

```bash
# List webcam
ls -l /dev/video*
v4l2-ctl --list-devices

# Install v4l-utils jika perlu
sudo apt-get install v4l-utils
```

---

## 🎯 Auto-Start on Boot (Optional)

Jika ingin aplikasi otomatis jalan saat boot, lihat panduan di **[RUN_ON_RASPI.md](RUN_ON_RASPI.md)** bagian "Auto-Start on Boot".

---

## 📊 Monitoring

```bash
# Cek status services
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-web

# Lihat logs
sudo journalctl -u drowsiness-backend -f

# Cek resource usage
htop

# Cek temperature
vcgencmd measure_temp
```

---

## ✅ Checklist

- [ ] Git sudah terinstall di Raspberry Pi
- [ ] Repository berhasil di-clone
- [ ] File `best_model.h5` ada di folder project
- [ ] Virtual environment sudah dibuat
- [ ] Dependencies sudah terinstall (termasuk `flask-cors`)
- [ ] Backend server berjalan di port 5001
- [ ] Web server berjalan di port 8000
- [ ] Bisa akses dari browser
- [ ] Webcam terdeteksi
- [ ] **CORS error sudah hilang!**

---

## 🆘 Quick Commands Reference

```bash
# Clone repository
git clone https://github.com/entung-prog/deteksikantuk.git

# Update repository
cd ~/deteksikantuk
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Run backend
python backend_server.py

# Run web server
python3 -m http.server 8000

# Check IP
hostname -I

# Test API
curl http://localhost:5001/api/health
```

---

## 📚 Panduan Lainnya

- **[RUN_ON_RASPI.md](RUN_ON_RASPI.md)** - Panduan lengkap deployment
- **[QUICK_RASPI.md](QUICK_RASPI.md)** - Quick reference
- **[SIMPLE_DEPLOY.md](SIMPLE_DEPLOY.md)** - Deployment dengan SCP

---

**Happy Coding! 🎉**
