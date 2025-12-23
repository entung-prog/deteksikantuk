# 🔄 Update Repository yang Sudah Ada di Raspberry Pi

## Situasi
Anda sudah punya clone repository di Raspberry Pi sebelumnya, tapi sekarang ada update baru (termasuk file model `best_model.h5` dan dokumentasi lengkap).

---

## ⚡ Cara Update (3 Langkah)

### **Step 1: SSH ke Raspberry Pi**

```bash
ssh entung@192.168.0.108
```

---

### **Step 2: Masuk ke Folder Repository**

```bash
# Masuk ke folder repository yang sudah ada
cd ~/deteksikantuk

# Atau jika nama foldernya berbeda, sesuaikan:
# cd ~/drowsiness-detection
# cd ~/web_test
```

---

### **Step 3: Pull Update Terbaru**

```bash
# Pull semua perubahan terbaru dari GitHub
git pull origin main
```

**Output yang benar:**
```
From https://github.com/entung-prog/deteksikantuk
 * branch            main       -> FETCH_HEAD
Updating 78a746c..3d4749c
Fast-forward
 CAMERA_SETUP.md                  | 95 ++++++++++++++++++
 CLONE_RASPI.md                   | 245 +++++++++++++++++++++++++++++++++++++++++++
 ... (banyak file lainnya)
 best_model.h5                    | Bin 0 -> 11435176 bytes
 35 files changed, 1234 insertions(+)
```

---

### **Step 4: Verify File Model Ada**

```bash
# Cek file model sudah ter-download
ls -lh best_model.h5

# Output yang benar:
# -rw-r--r-- 1 entung entung 11M Dec 24 01:20 best_model.h5
```

---

## ✅ Selesai! Sekarang Jalankan Aplikasi

```bash
# Activate virtual environment (jika sudah pernah dibuat)
source venv/bin/activate

# Atau buat baru jika belum ada
python3 -m venv venv
source venv/bin/activate

# Install/update dependencies
pip install flask flask-cors opencv-python numpy pillow

# Run backend (Terminal 1)
python backend_server.py

# Run web server (Terminal 2 - SSH baru)
python3 -m http.server 8000
```

---

## 🌐 Akses Aplikasi

```
http://192.168.0.108:8000/drowsiness_test.html
```

---

## 🔧 Troubleshooting

### ❌ **Error: Your local changes would be overwritten**

**Penyebab:** Ada perubahan lokal yang belum di-commit

**Solusi 1 - Simpan perubahan lokal:**
```bash
git stash
git pull origin main
git stash pop
```

**Solusi 2 - Buang perubahan lokal (hati-hati!):**
```bash
git reset --hard HEAD
git pull origin main
```

---

### ❌ **Error: Merge conflict**

**Solusi - Keep remote version (dari GitHub):**
```bash
git pull origin main
# Jika ada conflict, resolve dengan keep remote version:
git checkout --theirs .
git add .
git commit -m "Update from remote"
```

---

### ❌ **Error: fatal: not a git repository**

**Penyebab:** Folder bukan git repository

**Solusi - Clone baru:**
```bash
cd ~
git clone https://github.com/entung-prog/deteksikantuk.git
cd deteksikantuk
```

---

### ❌ **Model file tidak ter-download**

**Cek ukuran file:**
```bash
ls -lh best_model.h5
```

**Jika ukuran 0 atau tidak ada, download manual:**
```bash
# Option 1: Pull lagi dengan force
git fetch --all
git reset --hard origin/main

# Option 2: Copy manual dari Windows
# Di Windows PowerShell:
# scp best_model.h5 entung@192.168.0.108:~/deteksikantuk/
```

---

## 📊 Cek Status Update

```bash
# Lihat commit terbaru
git log --oneline -5

# Output yang benar:
# 3d4749c (HEAD -> main, origin/main) Resolve merge conflicts
# f814c45 Add all project files including model
# 8d7cbf5 add model
# 78a746c first commit

# Cek file apa saja yang berubah
git diff --name-only HEAD~3 HEAD

# Cek ukuran total repository
du -sh .
```

---

## 🎯 Summary

| Action | Command |
|--------|---------|
| **Update repository** | `git pull origin main` |
| **Check model file** | `ls -lh best_model.h5` |
| **Run backend** | `python backend_server.py` |
| **Run web server** | `python3 -m http.server 8000` |
| **Access app** | `http://192.168.0.108:8000/drowsiness_test.html` |

---

## ✅ Checklist

- [ ] SSH ke Raspberry Pi
- [ ] Masuk ke folder repository
- [ ] `git pull origin main` berhasil
- [ ] File `best_model.h5` ada (~11.4 MB)
- [ ] Virtual environment aktif
- [ ] Dependencies terinstall
- [ ] Backend running di port 5001
- [ ] Web server running di port 8000
- [ ] Bisa akses dari browser
- [ ] **CORS error sudah hilang!**

---

**Selamat! Repository Anda sudah up-to-date!** 🎉
