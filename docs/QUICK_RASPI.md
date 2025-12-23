# ⚡ Quick Reference - Run di Raspi

## 🎯 Masalah CORS - SOLVED!

**Penyebab:** `flask-cors` belum terinstall di Raspberry Pi

**Solusi:** Install `flask-cors` (sudah ada di `requirements.txt`)

---

## 📝 3 Langkah Cepat

### **1. Copy Files**
```powershell
# Windows
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
.\copy_to_pi.ps1 -PiIP "192.168.0.108"
```

### **2. Install di Raspi**
```bash
# SSH ke Raspi
ssh entung@192.168.0.108

cd ~/drowsiness-detection

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (TERMASUK flask-cors!)
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install pillow==10.1.0
```

### **3. Jalankan**
```bash
# Terminal 1 - Backend
source venv/bin/activate
python backend_server.py

# Terminal 2 - Web Server (SSH baru)
cd ~/drowsiness-detection
python3 -m http.server 8000
```

---

## 🌐 Akses

```
http://192.168.0.108:8000/drowsiness_test.html
```

---

## ✅ Kenapa CORS Error Hilang?

1. **`backend_server.py` sudah include:**
   ```python
   from flask_cors import CORS
   app = Flask(__name__)
   CORS(app)  # ← Ini yang handle CORS!
   ```

2. **`requirements.txt` sudah include:**
   ```
   flask-cors==4.0.0
   ```

3. **Setelah install `flask-cors`, CORS otomatis teratasi!**

---

## 🔧 Troubleshooting Cepat

### CORS Error masih muncul?
```bash
source venv/bin/activate
pip install flask-cors==4.0.0
# Restart backend
```

### Module not found?
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Webcam tidak terdeteksi?
```bash
ls -l /dev/video*
v4l2-ctl --list-devices
```

---

**Lihat panduan lengkap:** [RUN_ON_RASPI.md](RUN_ON_RASPI.md)
