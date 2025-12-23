# ⚡ SOLUSI CEPAT - Model Gagal di Raspi

## ❌ Error
```
Building model... GAGAL
```

## ✅ SOLUSI TERCEPAT: Increase Swap Memory

### **Di Raspberry Pi (SSH):**

```bash
# 1. Stop swap
sudo dphys-swapfile swapoff

# 2. Edit config
sudo nano /etc/dphys-swapfile
```

**Ubah:**
```
CONF_SWAPSIZE=2048  ← Dari 100 ke 2048
```

Save: `Ctrl+X`, `Y`, `Enter`

```bash
# 3. Restart swap
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 4. Verify
free -h
# Swap harus 2.0G!

# 5. Jalankan backend
cd ~/deteksikantuk
source venv/bin/activate
python backend_server.py
```

**Tunggu 2-5 menit untuk loading model!**

---

## ✅ Solusi Alternatif: Backend Optimized

```bash
# Copy file baru dari Windows
# scp backend_server_optimized.py entung@192.168.0.108:~/deteksikantuk/

# Jalankan
python backend_server_optimized.py
```

---

## 📊 Kenapa Gagal?

| Masalah | Solusi |
|---------|--------|
| RAM tidak cukup | Increase swap ke 2GB |
| TensorFlow berat | Gunakan backend optimized |
| Loading lama | Normal! Tunggu 2-5 menit |

---

## ✅ Checklist

- [ ] Swap sudah 2GB (`free -h`)
- [ ] Aplikasi lain di-close
- [ ] Tunggu 2-5 menit saat loading
- [ ] Lihat "✅ Model loaded successfully!"

---

**Panduan lengkap:** [FIX_MODEL_RASPI.md](FIX_MODEL_RASPI.md)

**Coba increase swap dulu! Paling efektif!** 🚀
