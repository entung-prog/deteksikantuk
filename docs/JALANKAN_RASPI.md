# ✅ Langkah-Langkah Lengkap - Jalankan di Raspi

## 🎯 Urutan yang Benar (PENTING!)

Anda sudah `git pull` ✅  
Sekarang ikuti urutan ini **step by step**:

---

## 📝 Step 1: Setup Virtual Environment

```bash
cd ~/deteksikantuk

# Buat virtual environment (jika belum ada)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Output yang benar:**
```
(venv) entung@raspberrypi:~/deteksikantuk$
```
Lihat ada `(venv)` di awal prompt!

---

## 📝 Step 2: Install CORS DULU! (WAJIB!)

```bash
# Pastikan venv aktif (ada tulisan (venv) di prompt)
pip install flask-cors==4.0.0
```

**Output yang benar:**
```
Successfully installed flask-cors-4.0.0
```

> [!IMPORTANT]
> **INI YANG MENGATASI CORS ERROR!** Jangan skip step ini!

---

## 📝 Step 3: Install Dependencies Lainnya

```bash
# Install Flask
pip install flask==3.0.0

# Install OpenCV
pip install opencv-python==4.8.1.78

# Install NumPy
pip install numpy==1.24.3

# Install Pillow
pip install pillow==10.1.0
```

**Atau install semua sekaligus:**
```bash
pip install flask==3.0.0 flask-cors==4.0.0 opencv-python==4.8.1.78 numpy==1.24.3 pillow==10.1.0
```

---

## 📝 Step 4: Verify Model File Ada

```bash
ls -lh best_model.h5
```

**Output yang benar:**
```
-rw-r--r-- 1 entung entung 11M Dec 24 01:20 best_model.h5
```

Jika tidak ada atau ukuran 0:
```bash
git pull origin main
```

---

## 📝 Step 5: Jalankan Backend Server

```bash
# Pastikan masih di folder deteksikantuk
# Pastikan venv masih aktif (ada tulisan (venv))
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

> [!TIP]
> **JANGAN TUTUP TERMINAL INI!** Backend harus tetap running.

---

## 📝 Step 6: Jalankan Web Server (Terminal Baru)

**Buka SSH baru:**
```bash
ssh entung@192.168.0.108
cd ~/deteksikantuk
python3 -m http.server 8000
```

**Output yang benar:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

> [!TIP]
> **JANGAN TUTUP TERMINAL INI JUGA!** Web server harus tetap running.

---

## 📝 Step 7: Test Backend API

**Buka SSH baru (Terminal 3):**
```bash
curl http://localhost:5001/api/health
```

**Output yang benar:**
```json
{"model_loaded":true,"status":"ok"}
```

✅ Jika dapat response ini, backend sudah OK!

---

## 📝 Step 8: Akses dari Browser

**Dari komputer/laptop Anda:**
```
http://192.168.0.108:8000/drowsiness_test.html
```

**Ganti IP sesuai Raspberry Pi Anda:**
```bash
# Cek IP di Raspberry Pi
hostname -I
```

---

## ✅ Checklist - Pastikan Semua Step Dilakukan!

- [ ] Virtual environment dibuat (`python3 -m venv venv`)
- [ ] Virtual environment aktif (`source venv/bin/activate`)
- [ ] **flask-cors SUDAH DIINSTALL** ← PENTING!
- [ ] Dependencies lain sudah diinstall
- [ ] File `best_model.h5` ada (~11.4 MB)
- [ ] Backend running di Terminal 1 (port 5001)
- [ ] Web server running di Terminal 2 (port 8000)
- [ ] API health check return `{"model_loaded":true,"status":"ok"}`
- [ ] Bisa akses dari browser
- [ ] **CORS error TIDAK MUNCUL!**

---

## 🔧 Troubleshooting

### ❌ Error: ModuleNotFoundError: No module named 'flask_cors'

**Penyebab:** Lupa install flask-cors atau venv tidak aktif

**Solusi:**
```bash
source venv/bin/activate  # Activate venv dulu!
pip install flask-cors==4.0.0
# Restart backend server (Ctrl+C lalu python backend_server.py lagi)
```

---

### ❌ Error: CORS policy blocked

**Penyebab:** flask-cors belum terinstall atau backend belum di-restart

**Solusi:**
```bash
# Di terminal backend (Terminal 1)
Ctrl + C  # Stop backend

source venv/bin/activate
pip install flask-cors==4.0.0
python backend_server.py  # Start lagi
```

---

### ❌ Error: Model file not found

**Solusi:**
```bash
ls -lh best_model.h5
# Jika tidak ada:
git pull origin main
```

---

### ❌ Error: Address already in use (port 5001 atau 8000)

**Solusi:**
```bash
# Kill process di port 5001
sudo lsof -ti:5001 | xargs sudo kill -9

# Kill process di port 8000
sudo lsof -ti:8000 | xargs sudo kill -9
```

---

## 🛑 Cara Stop Aplikasi

```bash
# Di Terminal 1 (Backend)
Ctrl + C

# Di Terminal 2 (Web Server)
Ctrl + C
```

---

## 🔄 Cara Restart Aplikasi

```bash
# Terminal 1 - Backend
cd ~/deteksikantuk
source venv/bin/activate
python backend_server.py

# Terminal 2 - Web Server (SSH baru)
cd ~/deteksikantuk
python3 -m http.server 8000
```

---

## 📊 Quick Commands Reference

```bash
# Activate venv
source venv/bin/activate

# Install CORS (WAJIB!)
pip install flask-cors==4.0.0

# Run backend
python backend_server.py

# Run web server (terminal baru)
python3 -m http.server 8000

# Test API
curl http://localhost:5001/api/health

# Check IP
hostname -I

# Stop (Ctrl+C di masing-masing terminal)
```

---

**Ikuti step by step, jangan skip! Terutama install flask-cors!** 🚀
