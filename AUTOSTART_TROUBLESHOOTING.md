# Troubleshooting: Autostart Berjalan Tapi Tidak Mendeteksi

## Masalah
Service `drowsiness-auto` berjalan (running) tapi **tidak mendeteksi kantuk**.

## Kemungkinan Penyebab

### 1. **Kamera Tidak Terinisialisasi**
Auto-detection thread **hanya dimulai jika kamera berhasil diinisialisasi**.

**Cara Cek:**
```bash
# Lihat log saat startup
sudo journalctl -u drowsiness-auto -n 100 | grep -i camera

# Yang HARUS muncul:
# ✅ USB Camera initialized at /dev/video0
# ATAU
# ✅ Raspberry Pi Camera Module initialized (picamera2)
```

**Jika TIDAK muncul:**
- Kamera tidak terdeteksi
- Auto-detection thread **TIDAK akan jalan**
- Web interface akan muncul tapi tidak ada deteksi

**Solusi:**
```bash
# Cek apakah kamera terdeteksi
ls -la /dev/video*

# Jika tidak ada, cek koneksi kamera
# Untuk USB webcam: pastikan terpasang dengan baik
# Untuk Pi Camera: pastikan kabel ribbon terpasang dan enabled di raspi-config
```

---

### 2. **Model Tidak Terload**
Jika model TFLite gagal load, deteksi tidak akan berjalan.

**Cara Cek:**
```bash
# Lihat log model loading
sudo journalctl -u drowsiness-auto -n 100 | grep -i model

# Yang HARUS muncul:
# ✅ Model loaded: /home/entung/deteksikantuk/backend/best_model_compatible.tflite
```

**Jika TIDAK muncul:**
```bash
# Cek apakah file model ada
ls -lh ~/deteksikantuk/backend/best_model_compatible.tflite

# Jika tidak ada, copy dari local machine
# Atau gunakan model alternatif
```

---

### 3. **Detection Thread Tidak Jalan**
Thread auto-detection mungkin crash atau tidak dimulai.

**Cara Cek:**
```bash
# Lihat log detection thread
sudo journalctl -u drowsiness-auto -n 100 | grep -i "auto-detection"

# Yang HARUS muncul:
# 🤖 Auto-detection thread started
# ✅ Auto-detection enabled
```

**Jika TIDAK muncul:**
- Thread tidak dimulai karena kamera atau model gagal load
- Ada error yang menyebabkan thread crash

**Solusi:**
```bash
# Lihat semua error di log
sudo journalctl -u drowsiness-auto -n 200 | grep -i error

# Atau lihat log lengkap
tail -f /var/log/drowsiness/drowsiness-auto-error.log
```

---

### 4. **Cascade Classifier Tidak Ditemukan**
Face detection memerlukan Haar Cascade file.

**Cara Cek:**
```bash
sudo journalctl -u drowsiness-auto -n 100 | grep -i cascade

# Yang HARUS muncul:
# ✅ Face cascade loaded from: /usr/share/opencv4/haarcascades/...
```

**Jika TIDAK muncul:**
```bash
# Install opencv data files
sudo apt-get install -y opencv-data

# Atau cari manual
find /usr -name "haarcascade_frontalface_default.xml" 2>/dev/null
```

---

## Langkah Diagnostik Lengkap

### Step 1: Cek Status Service
```bash
sudo systemctl status drowsiness-auto
```

**Expected:**
- `Active: active (running)`
- Tidak ada error merah

---

### Step 2: Lihat Log Startup
```bash
sudo journalctl -u drowsiness-auto -n 100 --no-pager
```

**Checklist yang HARUS ada:**
```
✅ Camera Type: opencv (atau picamera2)
✅ Model loaded
✅ Face cascade loaded
✅ Auto-detection enabled
🤖 Auto-detection thread started
🎥 Frame capture thread started
```

**Jika ada yang MISSING:**
- Itu adalah penyebab masalahnya!

---

### Step 3: Test Manual (Tanpa Service)
```bash
# Stop service dulu
sudo systemctl stop drowsiness-auto

# SSH ke Raspberry Pi
ssh entung@192.168.18.150

# Jalankan manual
cd ~/deteksikantuk/backend
source venv/bin/activate
python3 app_auto.py
```

**Perhatikan output:**
- Apakah kamera terdeteksi?
- Apakah model terload?
- Apakah ada error?

**Jika manual jalan tapi service tidak:**
- Masalah di konfigurasi systemd
- Mungkin environment variable atau path

---

### Step 4: Cek Web Interface
```bash
# Buka di browser
http://192.168.18.150:5000
```

**Periksa:**
1. **Video feed** - apakah muncul?
   - Jika TIDAK: kamera tidak terinisialisasi
2. **System Info panel** - lihat status:
   - Camera: harus ada (USB/picamera2)
   - Model: harus "Loaded ✓"
   - Hardware: boleh "Disabled ✗" (jika GPIO tidak tersedia)
3. **Statistics** - apakah angka berubah?
   - Total detections harus naik
   - Jika 0 terus: detection thread tidak jalan

---

## Solusi Umum

### Solusi 1: Restart Service
```bash
sudo systemctl restart drowsiness-auto
sudo journalctl -u drowsiness-auto -f
```

### Solusi 2: Reinstall Dependencies
```bash
cd ~/deteksikantuk/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Solusi 3: Cek Permission Kamera
```bash
# Tambahkan user ke group video
sudo usermod -a -G video $USER

# Logout dan login lagi
```

### Solusi 4: Enable Pi Camera (jika pakai Pi Camera)
```bash
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Solusi 5: Tambahkan Logging Debug
Edit `app_auto.py` untuk menambah logging:

```python
# Di bagian auto_detection_loop(), tambahkan:
logger.info(f"🔍 Detection loop iteration - frame available: {output_frame is not None}")
```

Lalu restart service dan lihat log.

---

## Quick Diagnostic Script

Buat file `check_autostart.sh`:

```bash
#!/bin/bash
echo "=== Drowsiness Auto-Detection Diagnostic ==="
echo ""

echo "1. Service Status:"
sudo systemctl is-active drowsiness-auto
echo ""

echo "2. Camera Devices:"
ls -la /dev/video* 2>/dev/null || echo "No camera found"
echo ""

echo "3. Model File:"
ls -lh ~/deteksikantuk/backend/best_model_compatible.tflite 2>/dev/null || echo "Model not found"
echo ""

echo "4. Recent Logs (last 20 lines):"
sudo journalctl -u drowsiness-auto -n 20 --no-pager
echo ""

echo "5. Checking for critical messages:"
sudo journalctl -u drowsiness-auto -n 100 --no-pager | grep -E "(Camera|Model|detection thread|ERROR|WARN)"
echo ""

echo "=== End of Diagnostic ==="
```

Jalankan:
```bash
chmod +x check_autostart.sh
./check_autostart.sh
```

---

## Kesimpulan

**Masalah paling umum:**
1. ❌ Kamera tidak terdeteksi → Auto-detection tidak jalan
2. ❌ Model tidak terload → Prediction gagal
3. ❌ Cascade tidak ditemukan → Face detection gagal

**Cara memastikan semuanya OK:**
```bash
# Harus muncul semua ini di log:
sudo journalctl -u drowsiness-auto -n 100 | grep "✅"

# Expected output:
# ✅ USB Camera initialized at /dev/video0
# ✅ Model loaded: .../best_model_compatible.tflite
# ✅ Face cascade loaded from: ...
# ✅ Auto-detection enabled
```

**Jika semua ✅ muncul tapi masih tidak deteksi:**
- Buka web interface dan lihat statistics
- Jika Total = 0: ada bug di detection loop
- Jika Total > 0: deteksi jalan, mungkin threshold terlalu tinggi/rendah
