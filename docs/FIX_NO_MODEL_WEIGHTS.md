# 🔧 Fix "No Model Weights Found" Error

## ❌ Error yang Muncul

```
Building model...
Building model architecture...
❌ No model weights found!
```

---

## 🔍 Penyebab

Backend mencoba load model dengan urutan:
1. Load `best_model.h5` (full model)
2. Jika gagal, build architecture dan load `../model_weights.weights.h5`
3. Jika `model_weights.weights.h5` tidak ada → Error!

---

## ✅ Solusi 1: Verify File Model Ada (CEPAT!)

### **Di Raspberry Pi:**

```bash
cd ~/deteksikantuk

# Cek apakah best_model.h5 ada
ls -lh best_model.h5

# Output yang benar:
# -rw-r--r-- 1 entung entung 11M Dec 24 01:20 best_model.h5
```

**Jika file tidak ada atau ukuran 0:**
```bash
# Pull lagi dari GitHub
git pull origin main

# Atau copy manual dari Windows
# Di Windows PowerShell:
# scp best_model.h5 entung@192.168.0.108:~/deteksikantuk/
```

---

## ✅ Solusi 2: Cek Error Detail

### **Jalankan backend dengan error detail:**

```bash
cd ~/deteksikantuk
source venv/bin/activate
python3 -c "
import tensorflow as tf
print('TensorFlow version:', tf.__version__)
try:
    model = tf.keras.models.load_model('best_model.h5')
    print('✅ Model loaded successfully!')
except Exception as e:
    print('❌ Error:', e)
"
```

**Kemungkinan error:**

### **Error 1: "OSError: Unable to open file"**
→ File `best_model.h5` tidak ada atau corrupt

**Solusi:**
```bash
# Re-download dari GitHub
git pull origin main

# Atau copy manual
```

### **Error 2: "Illegal instruction"**
→ TensorFlow tidak kompatibel dengan Raspberry Pi

**Solusi:**
```bash
# Uninstall TensorFlow
pip uninstall tensorflow

# Install versi kompatibel
pip install tensorflow==2.15.0
```

### **Error 3: "Cannot allocate memory"**
→ RAM tidak cukup

**Solusi:**
```bash
# Increase swap memory
sudo nano /etc/dphys-swapfile
# Ubah CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## ✅ Solusi 3: Gunakan Backend Optimized

```bash
cd ~/deteksikantuk
source venv/bin/activate
python backend_server_optimized.py
```

Backend optimized punya error handling lebih baik!

---

## ✅ Solusi 4: Fix Backend Script

Saya sudah buat versi backend yang lebih baik error handlingnya.

**Update backend_server.py:**

```python
# Line 39-66, ganti dengan:
print("="*60)
print("🔄 Loading model...")
print("="*60)

# Check if model file exists
if not os.path.exists(WEIGHTS_PATH):
    print(f"❌ ERROR: Model file not found!")
    print(f"   Looking for: {os.path.abspath(WEIGHTS_PATH)}")
    print(f"\n💡 Solutions:")
    print(f"   1. Run: git pull origin main")
    print(f"   2. Copy model: scp best_model.h5 user@raspi:~/deteksikantuk/")
    print(f"   3. Check file exists: ls -lh best_model.h5")
    model = None
else:
    try:
        print(f"📦 Loading model from: {WEIGHTS_PATH}")
        model = keras.models.load_model(WEIGHTS_PATH)
        print("✅ Model loaded successfully!")
        print(f"   Input shape: {model.input_shape}")
        print(f"   Output shape: {model.output_shape}")
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        print(f"\n💡 Try:")
        print(f"   1. Increase swap: sudo nano /etc/dphys-swapfile")
        print(f"   2. Use optimized backend: python backend_server_optimized.py")
        model = None
```

---

## 🔍 Debug Checklist

```bash
# 1. Cek file ada
ls -lh best_model.h5

# 2. Cek ukuran file (harus ~11MB)
du -h best_model.h5

# 3. Cek TensorFlow terinstall
python3 -c "import tensorflow; print(tensorflow.__version__)"

# 4. Cek memory available
free -h

# 5. Cek swap
swapon --show
```

---

## 📊 Expected vs Actual

| Check | Expected | Command |
|-------|----------|---------|
| **File exists** | Yes | `ls best_model.h5` |
| **File size** | ~11 MB | `ls -lh best_model.h5` |
| **TensorFlow** | 2.15.0 | `pip show tensorflow` |
| **Swap** | 2.0G | `free -h` |
| **Memory** | >500MB free | `free -h` |

---

## 🚀 Quick Fix (Paling Cepat)

```bash
# 1. Verify file
cd ~/deteksikantuk
ls -lh best_model.h5

# 2. Jika file ada tapi error, increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Ubah: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 3. Jalankan backend optimized
source venv/bin/activate
python backend_server_optimized.py
```

---

## 💡 Tips

1. **Selalu cek file ada dulu** dengan `ls -lh best_model.h5`
2. **Increase swap** sebelum jalankan backend
3. **Gunakan backend_optimized.py** jika masih error
4. **Tunggu 2-5 menit** saat loading model (normal di Raspi!)

---

**Coba Solusi 1 dulu (verify file)!** 🎯
