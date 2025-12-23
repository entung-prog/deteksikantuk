# ⚡ Quick Fix - No Model Weights Found

## ❌ Error
```
❌ No model weights found!
```

## ✅ Solusi Cepat

### **1. Cek File Ada**
```bash
cd ~/deteksikantuk
ls -lh best_model.h5
```

**Jika tidak ada atau ukuran 0:**
```bash
git pull origin main
```

### **2. Increase Swap**
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Ubah: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### **3. Gunakan Backend Optimized**
```bash
source venv/bin/activate
python backend_server_optimized.py
```

---

## 🔍 Debug

```bash
# Test load model
python3 -c "import tensorflow as tf; tf.keras.models.load_model('best_model.h5')"
```

**Jika error "Illegal instruction":**
```bash
pip uninstall tensorflow
pip install tensorflow==2.15.0
```

---

**Panduan lengkap:** [FIX_NO_MODEL_WEIGHTS.md](FIX_NO_MODEL_WEIGHTS.md)
