# ⚡ Quick Clone - Raspberry Pi

## 🎯 3 Langkah Cepat

### **1. SSH ke Raspberry Pi**
```bash
ssh entung@192.168.0.108
```

### **2. Clone Repository**
```bash
# Clone dari GitHub
git clone https://github.com/entung-prog/deteksikantuk.git

# Masuk ke folder
cd deteksikantuk
```

### **3. Install & Run**
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv libopencv-dev

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages (TERMASUK flask-cors!)
pip install flask flask-cors opencv-python numpy pillow

# Run backend (Terminal 1)
python backend_server.py

# Run web server (Terminal 2 - SSH baru)
python3 -m http.server 8000
```

---

## 🌐 Akses
```
http://192.168.0.108:8000/drowsiness_test.html
```

---

## 🔄 Update Repository
```bash
cd ~/deteksikantuk
git pull origin main
```

---

## ⚠️ Jika Model File >100MB

**Model file tidak bisa di-push ke GitHub biasa!**

**Solusi: Copy manual dengan SCP**
```powershell
# Dari Windows
scp best_model.h5 entung@192.168.0.108:~/deteksikantuk/
```

---

## ✅ Keuntungan Clone vs SCP

| Metode | Keuntungan | Kekurangan |
|--------|-----------|------------|
| **Git Clone** | ✅ Mudah update (`git pull`)<br>✅ Track changes<br>✅ Tidak perlu copy manual | ❌ File >100MB perlu LFS/manual |
| **SCP** | ✅ Bisa copy file besar<br>✅ Langsung | ❌ Susah update<br>❌ Manual copy |

**Rekomendasi:** Clone repository + SCP untuk model file jika >100MB

---

**Panduan lengkap:** [CLONE_RASPI.md](CLONE_RASPI.md)
