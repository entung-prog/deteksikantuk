# ⚡ Quick Run - Jalankan di Raspi

## 🎯 Anda Sudah: `git pull` selesai

Sekarang jalankan aplikasinya!

---

## 📝 First Time Setup (URUTAN PENTING!)

```bash
cd ~/deteksikantuk

# 1. Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install CORS DULU! (WAJIB!)
pip install flask-cors==4.0.0

# 3. Install dependencies lainnya
pip install flask opencv-python numpy pillow
```

> **PENTING:** Install `flask-cors` dulu untuk mengatasi CORS error!

---

## 🚀 Jalankan Aplikasi

### **Terminal 1 - Backend**
```bash
cd ~/deteksikantuk
source venv/bin/activate
python backend_server.py
```

### **Terminal 2 - Web Server** (SSH baru)
```bash
cd ~/deteksikantuk
python3 -m http.server 8000
```

---

## 🌐 Akses

**Dari browser:**
```
http://192.168.0.108:8000/drowsiness_test.html
```

**Test API:**
```bash
curl http://localhost:5001/api/health
# Output: {"model_loaded":true,"status":"ok"}
```

---

## 🛑 Stop

```bash
# Ctrl + C di kedua terminal
```

---

## 🔧 Troubleshooting

### Module not found
```bash
source venv/bin/activate
pip install flask flask-cors
```

### CORS error
```bash
pip install flask-cors==4.0.0
# Restart backend
```

### Port in use
```bash
sudo lsof -ti:5001 | xargs sudo kill -9
sudo lsof -ti:8000 | xargs sudo kill -9
```

---

**Panduan lengkap:** [JALANKAN_RASPI.md](JALANKAN_RASPI.md)
