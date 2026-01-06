# Autostart Setup untuk App Auto

## Cara Setup Autostart di Raspberry Pi

Untuk membuat `app_auto.py` berjalan otomatis saat Raspberry Pi booting:

### 1. Copy file ke Raspberry Pi

```bash
# Dari komputer lokal
./sync_to_raspi.sh
```

### 2. SSH ke Raspberry Pi

```bash
ssh entung@192.168.18.150
```

### 3. Jalankan script autostart

```bash
cd ~/deteksikantuk/autostart
./setup_autostart_auto.sh
```

Script ini akan:
- ✅ Membuat systemd service `drowsiness-auto.service`
- ✅ Enable service untuk autostart saat boot
- ✅ Start service langsung
- ✅ Setup logging di `/var/log/drowsiness/`

### 4. Verifikasi

```bash
# Cek status service
sudo systemctl status drowsiness-auto

# Lihat log real-time
sudo journalctl -u drowsiness-auto -f
```

## Perintah Berguna

```bash
# Start service
sudo systemctl start drowsiness-auto

# Stop service
sudo systemctl stop drowsiness-auto

# Restart service
sudo systemctl restart drowsiness-auto

# Cek status
sudo systemctl status drowsiness-auto

# Lihat log
tail -f /var/log/drowsiness/drowsiness-auto.log

# Disable autostart (jika tidak mau auto)
sudo systemctl disable drowsiness-auto
```

## Cara Kerja

Setelah setup:
1. 🔌 Raspberry Pi dinyalakan
2. ⏳ Sistem boot
3. 🚀 Service `drowsiness-auto` otomatis start
4. 🎥 Kamera diinisialisasi
5. 🤖 Deteksi otomatis berjalan
6. 💡 LED siap memberikan feedback
7. 🌐 Web interface tersedia di `http://192.168.18.150:5000`

**Tidak perlu menekan tombol apapun!** Sistem langsung aktif dan monitoring.

## Troubleshooting

### Service gagal start

```bash
# Lihat error log
sudo journalctl -u drowsiness-auto -n 50

# Atau lihat file log
cat /var/log/drowsiness/drowsiness-auto-error.log
```

### Restart service setelah update code

```bash
sudo systemctl restart drowsiness-auto
```

### Test manual tanpa service

```bash
cd ~/deteksikantuk/backend
source venv/bin/activate
python3 app_auto.py
```
