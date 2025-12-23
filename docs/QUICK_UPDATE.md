# ⚡ Quick Update - Repository di Raspi

## 🎯 Situasi
Anda sudah punya clone repository di Raspberry Pi, sekarang perlu update dengan perubahan terbaru (termasuk model file).

---

## 📝 3 Langkah Cepat

```bash
# 1. SSH ke Raspberry Pi
ssh entung@192.168.0.108

# 2. Masuk ke folder repository
cd ~/deteksikantuk

# 3. Pull update terbaru
git pull origin main

# 4. Verify model file ada
ls -lh best_model.h5
# Output: -rw-r--r-- 1 entung entung 11M Dec 24 01:20 best_model.h5
```

---

## ✅ Selesai! Jalankan Aplikasi

```bash
# Activate venv
source venv/bin/activate

# Run backend
python backend_server.py

# Run web server (Terminal baru)
python3 -m http.server 8000
```

**Akses:** `http://192.168.0.108:8000/drowsiness_test.html`

---

## 🔧 Jika Ada Error

### Error: Local changes would be overwritten
```bash
git stash
git pull origin main
```

### Error: Merge conflict
```bash
git reset --hard origin/main
```

### Model file tidak ada
```bash
git fetch --all
git reset --hard origin/main
```

---

**Panduan lengkap:** [UPDATE_RASPI.md](UPDATE_RASPI.md)
