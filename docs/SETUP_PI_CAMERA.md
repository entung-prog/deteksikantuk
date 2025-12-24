# Setup Pi Camera v1.3 untuk Drowsiness Detection

## 🎯 Overview

Panduan lengkap setup Raspberry Pi Camera v1.3 untuk drowsiness detection.

---

## 📦 Step 1: Enable Pi Camera

Di Raspberry Pi:

```bash
# Enable camera interface
sudo raspi-config
```

Pilih:
1. **Interface Options**
2. **Legacy Camera** → **Enable** (untuk Pi Camera v1.3)
3. **Finish** → **Reboot**

Setelah reboot, test camera:
```bash
# Test camera
libcamera-hello

# Atau
raspistill -o test.jpg
```

---

## 📥 Step 2: Install Dependencies

```bash
cd ~/deteksikantuk
source venv/bin/activate

# Install picamera2 (untuk Pi Camera Module)
sudo apt-get update
sudo apt-get install -y python3-picamera2

# Install dependencies lainnya
pip install flask opencv-python-headless tflite-runtime
```

---

## 🚀 Step 3: Run Camera Stream

Di Raspberry Pi, buka **2 terminal**:

### Terminal 1: Backend Server
```bash
cd ~/deteksikantuk
source venv/bin/activate
python backend_server.py
```

Expected output:
```
🚀 DROWSINESS DETECTION BACKEND
Loading model: best_model.tflite
✅ Model loaded!
Server: http://0.0.0.0:5001
```

### Terminal 2: Camera Stream
```bash
cd ~/deteksikantuk
source venv/bin/activate
python camera_stream.py
```

Expected output:
```
📷 RASPBERRY PI CAMERA STREAMING SERVER
✅ Camera Type: picamera2

Camera stream available at:
  - http://192.168.0.108:8080
  - http://localhost:8080
```

---

## 🌐 Step 4: Access Web Interface

### Dari Laptop:

Buka browser dan akses:
```
http://192.168.0.108:8000/drowsiness_test.html
```

Di web interface:
1. Pilih **"Raspberry Pi Camera"** di dropdown
2. Klik **Start Detection**
3. System akan ambil video dari `http://192.168.0.108:8080/video_feed`

---

## 🔧 Troubleshooting

### Error: "Failed to initialize camera"

**Solusi 1: Enable Legacy Camera**
```bash
sudo raspi-config
# Interface Options → Legacy Camera → Enable
sudo reboot
```

**Solusi 2: Check Camera Connection**
```bash
# Check camera detected
vcgencmd get_camera

# Should show: supported=1 detected=1
```

**Solusi 3: Camera Permissions**
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Reboot
sudo reboot
```

### Error: "No module named 'picamera2'"

```bash
sudo apt-get install -y python3-picamera2
```

### Camera stream tidak muncul di web

**Check camera stream langsung:**
```bash
# Di browser, buka:
http://192.168.0.108:8080
```

Kalau muncul video, berarti camera OK. Problem di frontend.

---

## 📊 Architecture

```
┌─────────────────────┐
│  Laptop Browser     │
│  (192.168.0.108)    │
└──────────┬──────────┘
           │
           ├─→ http://192.168.0.108:8000  (Web Interface)
           │
           ├─→ http://192.168.0.108:5001  (Backend API)
           │
           └─→ http://192.168.0.108:8080  (Camera Stream)
                        │
                        ▼
              ┌─────────────────┐
              │  Pi Camera v1.3 │
              │  (picamera2)    │
              └─────────────────┘
```

---

## ✅ Checklist

- [ ] Enable Legacy Camera di raspi-config
- [ ] Reboot Raspberry Pi
- [ ] Test camera dengan `libcamera-hello`
- [ ] Install picamera2
- [ ] Run `backend_server.py` (Terminal 1)
- [ ] Run `camera_stream.py` (Terminal 2)
- [ ] Akses web dari laptop
- [ ] Pilih "Raspberry Pi Camera"
- [ ] Start detection

---

## 💡 Tips

- **Pi Camera v1.3** butuh **Legacy Camera** enabled
- **picamera2** lebih modern dari picamera (deprecated)
- Camera stream di port **8080**, backend di port **5001**
- Web interface di port **8000**

---

Selamat mencoba! 🚀
