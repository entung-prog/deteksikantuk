# 📖 Panduan Deployment Drowsiness Detection - Raspberry Pi 5

**Panduan Lengkap untuk Bimbingan Skripsi**

---

## 📌 Informasi Sistem

- **Raspberry Pi**: Raspberry Pi 5
- **IP Address**: `10.193.250.211`
- **Username**: `entung`
- **Folder Aplikasi**: `/home/entung/drowsiness-detection`
- **OS**: Raspberry Pi OS (Bookworm)

---

## 🎯 Arsitektur Sistem

```
┌─────────────┐         WiFi          ┌──────────────────┐
│   Laptop    │ ◄──────────────────► │  Raspberry Pi 5  │
│  (Browser)  │   10.193.250.x       │  10.193.250.211  │
└─────────────┘                       └──────────────────┘
      │                                        │
      │                                        ├─ Backend (Port 5001)
      │                                        ├─ Web Server (Port 8000)
      └────── HTTP Request ────────────────────┤
                                               └─ Camera Stream (Port 8080)
```

### Komponen:
1. **Frontend** (HTML/CSS/JS) - Berjalan di browser laptop
2. **Backend** (Flask/Python) - Berjalan di Raspberry Pi
3. **Model** (TensorFlow/Keras) - Diproses di Raspberry Pi
4. **Webcam** - Dari laptop (via browser WebRTC)

---

## 🚀 Quick Start

### 1. SSH ke Raspberry Pi

```powershell
ssh entung@10.193.250.211
```

### 2. Start Semua Services

```bash
cd ~/drowsiness-detection

# Kill process lama (jika ada)
pkill -f python

# Start backend (port 5001)
source venv/bin/activate
python backend_server.py &
deactivate

# Start web server (port 8000)
python3 -m http.server 8000 &

# Verify running
ps aux | grep python
```

### 3. Akses dari Browser

```
http://10.193.250.211:8000/drowsiness_test.html
```

---

## 📦 File Structure

```
/home/entung/drowsiness-detection/
├── backend_server.py          # Flask API server
├── drowsiness_test.html       # Web interface
├── drowsiness_test.css        # Styling
├── drowsiness_test_hybrid.js  # Frontend logic
├── best_model.h5             # TensorFlow model (~11MB)
├── requirements.txt          # Python dependencies
├── camera_stream.py          # Camera streaming server
└── venv/                     # Python virtual environment
```

---

## 🔧 Konfigurasi Port

| Service | Port | URL | Fungsi |
|---------|------|-----|--------|
| Backend API | 5001 | `http://10.193.250.211:5001/api` | Model inference |
| Web Server | 8000 | `http://10.193.250.211:8000` | Serve HTML/CSS/JS |
| Camera Stream | 8080 | `http://10.193.250.211:8080` | Stream kamera Pi |

---

## 💻 Command Reference

### Start Services

```bash
# Backend
cd ~/drowsiness-detection
source venv/bin/activate
python backend_server.py &
deactivate

# Web Server
python3 -m http.server 8000 &

# Camera Stream (optional)
python3 camera_stream.py &
```

### Stop Services

```bash
# Stop semua Python processes
pkill -f python

# Stop specific service
pkill -f backend_server
pkill -f "http.server"
pkill -f camera_stream
```

### Check Status

```bash
# Lihat running processes
ps aux | grep python

# Check ports
sudo lsof -i :5001  # Backend
sudo lsof -i :8000  # Web
sudo lsof -i :8080  # Camera

# Test backend health
curl http://localhost:5001/api/health
```

### System Info

```bash
# IP Address
hostname -I

# System resources
htop
df -h
free -h

# Temperature
vcgencmd measure_temp
```

---

## 🐛 Troubleshooting

### Problem 1: Port Already in Use

**Error:**
```
Address already in use
Port 5001 is in use by another program
```

**Solution:**
```bash
pkill -f backend_server
# atau
sudo lsof -i :5001
sudo kill -9 <PID>
```

---

### Problem 2: Cannot Connect to Backend

**Error di browser:**
```
Cannot connect to backend
```

**Solution:**
```bash
# Check backend running
ps aux | grep backend_server

# Restart backend
cd ~/drowsiness-detection
source venv/bin/activate
python backend_server.py

# Test
curl http://localhost:5001/api/health
```

---

### Problem 3: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask_cors'
```

**Solution:**
```bash
cd ~/drowsiness-detection
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem 4: Model Not Found

**Error:**
```
❌ No model weights found!
```

**Solution:**
```bash
# Check file
ls -lh ~/drowsiness-detection/best_model.h5

# Should be ~11MB
# If missing, copy from Windows:
# scp best_model.h5 entung@10.193.250.211:~/drowsiness-detection/
```

---

### Problem 5: IP Address Changed

**Symptoms:**
- SSH timeout
- Web tidak bisa diakses

**Solution:**
```bash
# Di Raspberry Pi
hostname -I

# Update semua URL dengan IP baru
```

---

### Problem 6: SSH Connection Refused

**Solution:**
```bash
# Di Raspberry Pi
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

---

## 📊 Cara Menggunakan Aplikasi

### 1. Visualization Mode

1. Buka `http://10.193.250.211:8000/drowsiness_test.html`
2. Klik **"Start Visualization"**
3. Izinkan browser akses webcam
4. Sistem akan mendeteksi drowsiness real-time
5. FPS dan confidence ditampilkan

### 2. Testing Mode

1. Klik **"Start Testing Mode"**
2. Data akan dicatat setiap interval (default 2 detik)
3. Hasil muncul di tabel
4. Klik **"Export CSV"** untuk download hasil

### 3. Settings

- **Drowsy Threshold**: Batas confidence (default 0.5)
- **Alarm Duration**: Waktu sebelum alarm (default 3 detik)
- **Capture Interval**: Interval capture di testing mode

---

## 🔄 Update Files

### Dari Windows ke Raspberry Pi

```powershell
# Copy single file
scp backend_server.py entung@10.193.250.211:~/drowsiness-detection/

# Copy multiple files
scp *.py entung@10.193.250.211:~/drowsiness-detection/
scp *.js entung@10.193.250.211:~/drowsiness-detection/
```

### Restart Services Setelah Update

```bash
# SSH ke Raspberry Pi
ssh entung@10.193.250.211

# Restart backend
pkill -f backend_server
cd ~/drowsiness-detection
source venv/bin/activate
python backend_server.py &
```

---

## 📈 Performance

### Expected Performance

- **FPS**: 5-15 fps (tergantung Raspberry Pi 5 load)
- **Latency**: ~100-200ms per frame
- **Accuracy**: Tergantung model training

### Optimization Tips

1. **Reduce resolution** - Edit backend untuk resize image lebih kecil
2. **Batch processing** - Process multiple frames sekaligus
3. **Model optimization** - Gunakan TFLite untuk inference lebih cepat
4. **Close unused services** - Matikan service yang tidak perlu

---

## 🔒 Security Notes

### Current Setup (Development)

- ⚠️ Flask debug mode: OFF
- ⚠️ No authentication
- ⚠️ HTTP (not HTTPS)
- ⚠️ CORS enabled untuk semua origin

### For Production

1. Enable HTTPS dengan SSL certificate
2. Add authentication (login system)
3. Restrict CORS ke domain tertentu
4. Use production WSGI server (Gunicorn/uWSGI)
5. Setup firewall rules
6. Regular security updates

---

## 📝 Maintenance Checklist

### Daily
- [ ] Check services running
- [ ] Monitor system temperature
- [ ] Check disk space

### Weekly
- [ ] Review logs
- [ ] Update system packages
- [ ] Backup configuration

### Monthly
- [ ] Full system update
- [ ] Review security
- [ ] Performance optimization

---

## 🎓 Untuk Bimbingan Dosen

### Poin-Poin Penting

1. **Arsitektur Hybrid**
   - Frontend di browser (laptop)
   - Backend di Raspberry Pi
   - Model inference di edge device

2. **Teknologi yang Digunakan**
   - Backend: Flask (Python)
   - Frontend: HTML5, JavaScript (WebRTC)
   - Model: TensorFlow/Keras (MobileNetV2)
   - Deployment: Raspberry Pi 5

3. **Fitur Utama**
   - Real-time drowsiness detection
   - Testing mode dengan logging
   - Export hasil ke CSV
   - Configurable threshold

4. **Kelebihan Sistem**
   - Low latency (~100-200ms)
   - Portable (edge computing)
   - Web-based (cross-platform)
   - Easy to deploy

5. **Limitasi**
   - Perlu WiFi connection
   - FPS terbatas (5-15 fps)
   - Webcam quality dependent
   - Single user per instance

---

## 📞 Quick Help

### Jika Ada Masalah

1. **Check logs** - Lihat terminal output
2. **Restart services** - Kill dan start ulang
3. **Check IP** - Pastikan IP tidak berubah
4. **Test connectivity** - Ping dan SSH
5. **Verify files** - Check semua file ada

### Common Commands

```bash
# Full restart
ssh entung@10.193.250.211
pkill -f python
cd ~/drowsiness-detection
source venv/bin/activate && python backend_server.py & deactivate
python3 -m http.server 8000 &

# Check everything
ps aux | grep python
sudo lsof -i :5001,8000
hostname -I
```

---

## ✅ Deployment Checklist

- [x] Raspberry Pi setup dan connected
- [x] SSH enabled dan accessible
- [x] Files tercopy ke Raspberry Pi
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Model file available (~11MB)
- [ ] Backend running (port 5001)
- [ ] Web server running (port 8000)
- [ ] Accessible dari browser laptop
- [ ] Drowsiness detection working

---

## 📚 Resources

### Documentation
- Flask: https://flask.palletsprojects.com/
- TensorFlow: https://www.tensorflow.org/
- Raspberry Pi: https://www.raspberrypi.com/documentation/

### Repository Structure
```
pipeline/
├── webtest/              # Deployment files
│   ├── backend_server.py
│   ├── drowsiness_test.html
│   ├── drowsiness_test_hybrid.js
│   └── requirements.txt
└── best_model.h5        # Trained model
```

---

**Last Updated**: 23 Desember 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
