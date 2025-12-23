# 🚀 Manual Deployment Guide - Raspberry Pi

Karena SSH connection timeout, gunakan metode manual ini.

## 📋 Yang Anda Butuhkan

- USB Flash Drive
- Akses langsung ke Raspberry Pi (monitor + keyboard)
- Atau akses via VNC/Remote Desktop jika sudah enabled

---

## 📦 Step 1: Copy Files ke USB

### Di Windows, jalankan PowerShell:

```powershell
# Ganti E: dengan drive letter USB Anda
$usbDrive = "E:"
$sourceDir = "c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest"

# Buat folder di USB
New-Item -Path "$usbDrive\drowsiness" -ItemType Directory -Force

# Copy application files
Copy-Item "$sourceDir\backend_server.py" -Destination "$usbDrive\drowsiness\"
Copy-Item "$sourceDir\drowsiness_test.html" -Destination "$usbDrive\drowsiness\"
Copy-Item "$sourceDir\drowsiness_test.css" -Destination "$usbDrive\drowsiness\"
Copy-Item "$sourceDir\drowsiness_test_hybrid.js" -Destination "$usbDrive\drowsiness\"
Copy-Item "$sourceDir\requirements.txt" -Destination "$usbDrive\drowsiness\"
Copy-Item "$sourceDir\deploy_manual.sh" -Destination "$usbDrive\drowsiness\"

# Copy model file
Copy-Item "c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\best_model.h5" -Destination "$usbDrive\drowsiness\"

Write-Host "Files copied to USB!" -ForegroundColor Green
```

**Atau copy manual:**
1. Buka folder `c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest`
2. Copy semua file ke USB drive
3. Copy juga `best_model.h5` dari folder parent

---

## 🔌 Step 2: Transfer ke Raspberry Pi

1. **Colokkan USB** ke Raspberry Pi
2. **Login ke Raspberry Pi** (monitor + keyboard)
3. **Mount USB** (biasanya auto-mount):

```bash
# Cek USB mount point
ls /media/pi/

# Atau manual mount jika perlu
sudo mount /dev/sda1 /mnt
```

4. **Copy files** ke home directory:

```bash
# Jika auto-mount
cp -r /media/pi/*/drowsiness /home/pi/drowsiness-detection

# Atau jika manual mount
cp -r /mnt/drowsiness /home/pi/drowsiness-detection

# Verify files
cd /home/pi/drowsiness-detection
ls -la
```

---

## ⚙️ Step 3: Run Deployment Script

Di Raspberry Pi:

```bash
cd /home/pi/drowsiness-detection
chmod +x deploy_manual.sh
./deploy_manual.sh
```

Script akan otomatis:
- ✅ Install dependencies
- ✅ Setup Python virtual environment
- ✅ Install packages
- ✅ Setup systemd services
- ✅ Start aplikasi

---

## ✅ Step 4: Verify

### Check services:

```bash
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-web
```

### Get IP address:

```bash
hostname -I
```

### Test dari browser:

```
http://<raspberry-pi-ip>:8000/drowsiness_test.html
```

Contoh: `http://192.168.0.108:8000/drowsiness_test.html`

---

## 🔧 Troubleshooting

### Jika service gagal start:

```bash
# Check logs
sudo journalctl -u drowsiness-backend -n 50
sudo journalctl -u drowsiness-web -n 50

# Restart services
sudo systemctl restart drowsiness-backend
sudo systemctl restart drowsiness-web
```

### Jika port sudah digunakan:

```bash
# Check what's using port 5000
sudo lsof -i :5000

# Check what's using port 8000
sudo lsof -i :8000
```

---

## 📱 Akses dari Device Lain

Setelah deployment berhasil:

1. **Cari IP Raspberry Pi**: `hostname -I`
2. **Buka browser** di device lain (laptop/phone)
3. **Akses**: `http://<pi-ip>:8000/drowsiness_test.html`

Pastikan device dan Raspberry Pi di network yang sama!

---

## 🎯 Next Steps

Setelah aplikasi running:
- Test webcam detection
- Test drowsiness detection
- Check FPS performance
- Verify model inference working

Good luck! 🚀
