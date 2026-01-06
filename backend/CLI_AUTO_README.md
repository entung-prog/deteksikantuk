# CLI Auto-Detection Mode

## Cara Pakai

Versi CLI ini lebih sederhana untuk testing - **tidak perlu web browser**, semua output di terminal.

### 1. Jalankan langsung di terminal

```bash
cd ~/deteksikantuk/backend
source venv/bin/activate
python3 app_auto_cli.py
```

### 2. Apa yang akan terjadi:

```
================================================================================
🚗 DROWSINESS DETECTION - CLI MODE
================================================================================

Initializing...
✅ USB Camera initialized at /dev/video0
Using tflite-runtime
✅ Model loaded: best_model_compatible.tflite
   Input shape: [1 224 224 3]
✅ Face cascade loaded
✅ Hardware initialized
   Buzzer: GPIO17
   RGB LED: R=GPIO22, G=GPIO27, B=GPIO24

================================================================================
✅ SYSTEM READY - Starting detection...
Press Ctrl+C to stop
================================================================================

[14:20:15] ✅ ALERT | Conf: 99.8% | Total: 45 | Drowsy: 0 | Alert: 45
```

### 3. Status yang ditampilkan:

- **🔍 NO FACE DETECTED** (kuning) - Tidak ada wajah terdeteksi
- **✅ ALERT** (hijau) - Mata terbuka, tidak mengantuk
- **😴 DROWSY** (kuning) - Mata tertutup, mengantuk
- **😴 DROWSY ⚠️ ALARM!** (merah) - Mengantuk lebih dari 3 detik

### 4. GPIO/LED akan otomatis:

- **LED Hijau** = Alert (mata terbuka)
- **LED Kuning** = Drowsy (mata tertutup < 3 detik)
- **LED Merah + Buzzer** = Alarm (mata tertutup ≥ 3 detik)

### 5. Stop dengan Ctrl+C

Akan menampilkan summary:

```
📊 SESSION SUMMARY
================================================================================
Runtime: 120.5s
Total detections: 1205
Drowsy: 45 (3.7%)
Alert: 1160 (96.3%)
================================================================================
✅ Done!
```

## Keuntungan CLI Mode

✅ **Lebih mudah troubleshooting** - langsung lihat error di terminal  
✅ **Tidak perlu browser** - cocok untuk SSH  
✅ **Real-time output** - lihat deteksi langsung  
✅ **Session statistics** - summary otomatis saat stop  
✅ **GPIO tetap jalan** - LED dan buzzer bekerja normal  

## Troubleshooting

### Jika kamera tidak terdeteksi:
```bash
ls /dev/video*
```

### Jika model tidak ditemukan:
```bash
ls -lh ~/deteksikantuk/backend/best_model_compatible.tflite
```

### Jika GPIO error (normal di local machine):
Script akan tetap jalan tanpa GPIO, hanya deteksi saja.

## Untuk Autostart

Jika ingin pakai versi CLI untuk autostart, edit service file:

```bash
sudo nano /etc/systemd/system/drowsiness-auto.service
```

Ganti `app_auto.py` dengan `app_auto_cli.py`:
```
ExecStart=/home/entung/deteksikantuk/backend/venv/bin/python3 /home/entung/deteksikantuk/backend/app_auto_cli.py
```

Lalu restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart drowsiness-auto
sudo journalctl -u drowsiness-auto -f
```
