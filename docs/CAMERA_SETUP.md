# 📷 Setup Kamera Raspberry Pi untuk Remote Access

## Masalah

Web browser hanya bisa akses webcam dari device yang menjalankan browser. Untuk menggunakan kamera Raspberry Pi dari laptop, kita perlu **streaming server**.

---

## ✅ Solusi: Camera Streaming Server

Saya sudah buatkan `camera_stream.py` yang akan stream kamera Raspberry Pi via HTTP.

### Step 1: Copy File ke Raspberry Pi

**Di Windows PowerShell:**

```powershell
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
scp camera_stream.py entung@192.168.0.108:~/drowsiness-detection/
```

### Step 2: Install Dependencies (jika perlu)

**Di SSH Raspberry Pi:**

```bash
cd ~/drowsiness-detection
source venv/bin/activate

# OpenCV sudah terinstall dari sebelumnya
# Jika belum:
pip install opencv-python
```

### Step 3: Enable Kamera Raspberry Pi

**Jika pakai Raspberry Pi Camera Module:**

```bash
# Enable camera
sudo raspi-config
# Pilih: Interface Options → Camera → Enable
# Reboot jika diminta

# Verify camera
vcgencmd get_camera
# Harus muncul: supported=1 detected=1
```

**Jika pakai USB Webcam:**

```bash
# Check USB camera
ls /dev/video*
# Harus muncul: /dev/video0

# Test camera
v4l2-ctl --list-devices
```

### Step 4: Start Camera Stream Server

**Di SSH Raspberry Pi:**

```bash
cd ~/drowsiness-detection
source venv/bin/activate

# Start camera streaming server
python camera_stream.py &
```

### Step 5: Akses Camera Stream

**Di browser laptop, buka:**

```
http://192.168.0.108:8080
```

Anda akan lihat live stream dari kamera Raspberry Pi!

---

## 🎯 Integrasi dengan Drowsiness Detection

Sekarang ada 2 opsi:

### Opsi A: Gunakan Webcam Laptop (Lebih Mudah)

- Akses: `http://192.168.0.108:8000/drowsiness_test.html`
- Gunakan webcam laptop untuk deteksi
- Backend di Raspberry Pi yang proses

### Opsi B: Stream Kamera Raspberry Pi

- Akses camera stream: `http://192.168.0.108:8080`
- Lihat live feed dari kamera Raspberry Pi
- Untuk deteksi, perlu modifikasi frontend (advanced)

---

## 🚀 Quick Commands

```bash
# Di Raspberry Pi - Start semua services

cd ~/drowsiness-detection
source venv/bin/activate

# Backend server (port 5001)
python backend_server.py &

# Web server (port 8000)
python -m http.server 8000 &

# Camera stream (port 8080)
python camera_stream.py &

# Check running services
ps aux | grep python
```

**Akses:**
- Drowsiness Detection: `http://192.168.0.108:8000/drowsiness_test.html`
- Camera Stream: `http://192.168.0.108:8080`

---

## 💡 Rekomendasi

**Untuk testing sekarang:**
- Gunakan **webcam laptop** (lebih mudah)
- Akses `http://192.168.0.108:8000/drowsiness_test.html`
- Backend Raspberry Pi yang proses deteksi

**Untuk production nanti:**
- Setup camera streaming
- Modifikasi frontend untuk consume camera stream
- Full remote monitoring

---

**Coba copy `camera_stream.py` dan jalankan untuk lihat stream kamera Raspberry Pi!** 📷
