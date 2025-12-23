# ✅ Solusi Alternatif - Fix Model Loading di Raspi

## ❌ Masalah: Model H5 Gagal Load di Raspberry Pi

Penyebab umum:
- TensorFlow terlalu berat
- RAM tidak cukup
- Dependencies tidak lengkap

---

## ✅ Solusi 1: Increase Swap Memory (RECOMMENDED)

Ini solusi paling mudah dan efektif!

### **Di Raspberry Pi:**

```bash
# 1. Stop swap
sudo dphys-swapfile swapoff

# 2. Edit config
sudo nano /etc/dphys-swapfile
```

**Ubah baris ini:**
```
# Dari:
CONF_SWAPSIZE=100

# Ke:
CONF_SWAPSIZE=2048
```

Save: `Ctrl+X`, `Y`, `Enter`

```bash
# 3. Setup swap baru
sudo dphys-swapfile setup

# 4. Start swap
sudo dphys-swapfile swapon

# 5. Verify
free -h
```

**Output yang benar:**
```
              total        used        free      shared  buff/cache   available
Mem:           1.8G        500M        1.0G         50M        300M        1.2G
Swap:          2.0G          0B        2.0G  ← Harus 2.0G!
```

### **Sekarang Jalankan Backend:**

```bash
cd ~/deteksikantuk
source venv/bin/activate
python backend_server.py
```

**Seharusnya berhasil sekarang!** ✅

---

## ✅ Solusi 2: Install TensorFlow yang Benar

```bash
cd ~/deteksikantuk
source venv/bin/activate

# Uninstall TensorFlow yang ada
pip uninstall tensorflow

# Install versi yang kompatibel
pip install tensorflow==2.15.0

# Atau gunakan TensorFlow Lite interpreter
pip install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
```

---

## ✅ Solusi 3: Gunakan Backend dengan Memory Limit

Saya sudah buat `backend_server_optimized.py` yang lebih hemat memory!

```bash
python backend_server_optimized.py
```

---

## ✅ Solusi 4: Close Aplikasi Lain

```bash
# Cek memory usage
free -h

# Cek process yang makan memory
htop

# Kill process yang tidak perlu
# Tekan F9 untuk kill di htop
```

---

## 🔧 Troubleshooting

### Error: "Illegal instruction"

**Solusi:**
```bash
# Install TensorFlow pre-built untuk ARM
pip3 install https://github.com/PINTO0309/Tensorflow-bin/releases/download/v2.15.0/tensorflow-2.15.0-cp39-cp39-linux_armv7l.whl
```

### Error: "Cannot allocate memory"

**Solusi:** Increase swap (Solusi 1)

### Model loading sangat lambat

**Normal!** Loading pertama kali bisa 2-5 menit di Raspberry Pi. Tunggu saja sampai muncul:
```
✅ Model loaded successfully!
```

---

## 📊 Checklist

- [ ] Swap memory sudah dinaikkan ke 2GB
- [ ] TensorFlow versi 2.15.0 terinstall
- [ ] Virtual environment aktif
- [ ] Aplikasi lain sudah di-close
- [ ] Tunggu 2-5 menit untuk model loading
- [ ] Backend berhasil start

---

## 💡 Tips

1. **Sabar saat loading model** - Bisa 2-5 menit di Raspberry Pi
2. **Jangan close terminal** saat model sedang loading
3. **Monitor memory** dengan `htop` di terminal lain
4. **Restart Raspberry Pi** jika masih error setelah increase swap

---

**Coba Solusi 1 dulu (increase swap)! Paling efektif!** 🚀
