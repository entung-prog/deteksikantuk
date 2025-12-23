# 🎯 PANDUAN LENGKAP - Drowsiness Detection Raspberry Pi 5

**Panduan Simple untuk Bimbingan Skripsi**

---

## 📌 INFORMASI PENTING

```
Raspberry Pi IP: 10.193.250.211
Username: entung
Password: mazdatiga098
Folder: /home/entung/drowsiness-detection
```

---

## 🚀 CARA MENJALANKAN APLIKASI

### **Step 1: SSH ke Raspberry Pi**

```powershell
# Di Windows PowerShell
ssh entung@10.193.250.211
# Password: mazdatiga098
```

### **Step 2: Start Semua Services**

```bash
# Di terminal SSH Raspberry Pi
cd ~/drowsiness-detection

# Kill process lama (jika ada)
pkill -f python

# Start Backend (port 5001)
source venv/bin/activate
python backend_server.py &
deactivate

# Start Web Server (port 8000)
python3 -m http.server 8000 &

# Start Camera Stream (port 8080)
python3 camera_stream.py &

# Check running
ps aux | grep python
```

### **Step 3: Akses dari Browser Laptop**

**Drowsiness Detection:**
```
http://10.193.250.211:8000/drowsiness_test.html
```

**Camera Stream:**
```
http://10.193.250.211:8080
```

---

## 🎮 CARA MENGGUNAKAN

### **Drowsiness Detection:**

1. Buka `http://10.193.250.211:8000/drowsiness_test.html`
2. Klik **"Start Visualization"**
3. Izinkan browser akses webcam laptop
4. Sistem akan deteksi drowsiness real-time
5. Klik **"Start Testing Mode"** untuk logging
6. Klik **"Export CSV"** untuk download hasil

### **Camera Stream:**

1. Buka `http://10.193.250.211:8080`
2. Lihat live feed dari kamera Raspberry Pi

---

## 🛑 CARA STOP APLIKASI

```bash
# SSH ke Raspberry Pi
ssh entung@10.193.250.211

# Stop semua services
pkill -f python
```

---

## 🔧 TROUBLESHOOTING

### **Problem: SSH Timeout**

```bash
# Di Raspberry Pi (monitor + keyboard)
hostname -I  # Cek IP baru

# Di Windows
ssh entung@<IP_BARU>
```

### **Problem: Port Already in Use**

```bash
# SSH ke Raspberry Pi
pkill -f python
# Lalu start ulang services
```

### **Problem: Cannot Connect to Backend**

```bash
# Check backend running
ps aux | grep backend_server

# Restart backend
cd ~/drowsiness-detection
source venv/bin/activate
python backend_server.py &
```

### **Problem: File Not Found (404)**

```bash
# Check file ada
ls ~/drowsiness-detection/drowsiness_test.html

# Restart web server
pkill -f http.server
cd ~/drowsiness-detection
python3 -m http.server 8000 &
```

---

## 📊 UNTUK DEMO BIMBINGAN

### **Yang Perlu Ditunjukkan:**

1. ✅ **Arsitektur Sistem**
   - Frontend: Browser (laptop)
   - Backend: Raspberry Pi
   - Model: TensorFlow di Raspberry Pi

2. ✅ **Fitur Utama**
   - Real-time drowsiness detection
   - Testing mode dengan data logging
   - Export hasil ke CSV
   - Camera streaming

3. ✅ **Teknologi**
   - Backend: Flask (Python)
   - Frontend: HTML5, JavaScript
   - Model: MobileNetV2 (TensorFlow)
   - Hardware: Raspberry Pi 5

### **Flow Demo:**

```
1. Tunjukkan SSH ke Raspberry Pi
   → ssh entung@10.193.250.211

2. Tunjukkan services running
   → ps aux | grep python

3. Buka browser, akses aplikasi
   → http://10.193.250.211:8000/drowsiness_test.html

4. Demo drowsiness detection
   → Start Visualization
   → Tunjukkan deteksi real-time

5. Demo testing mode
   → Start Testing Mode
   → Tunjukkan data logging
   → Export CSV

6. Tunjukkan camera stream
   → http://10.193.250.211:8080
```

---

## 📁 FILE PENTING

### **Di Windows:**
```
c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest\
├── backend_server.py
├── drowsiness_test.html
├── drowsiness_test_hybrid.js
├── camera_stream.py
├── requirements.txt
└── DEPLOYMENT_GUIDE.md  ← PANDUAN INI
```

### **Di Raspberry Pi:**
```
/home/entung/drowsiness-detection/
├── backend_server.py
├── drowsiness_test.html
├── drowsiness_test_hybrid.js
├── camera_stream.py
├── best_model.h5  (~11MB)
└── venv/  (virtual environment)
```

---

## 🎯 QUICK COMMANDS

### **Start Everything:**
```bash
ssh entung@10.193.250.211
cd ~/drowsiness-detection
pkill -f python
source venv/bin/activate && python backend_server.py & deactivate
python3 -m http.server 8000 &
python3 camera_stream.py &
```

### **Check Status:**
```bash
ps aux | grep python
sudo lsof -i :5001,8000,8080
hostname -I
```

### **Stop Everything:**
```bash
pkill -f python
```

---

## 📞 JIKA ADA MASALAH

### **Cek IP Berubah:**
```bash
# Di Raspberry Pi
hostname -I
```

### **Restart Semua:**
```bash
ssh entung@10.193.250.211
pkill -f python
cd ~/drowsiness-detection
source venv/bin/activate && python backend_server.py & deactivate
python3 -m http.server 8000 &
python3 camera_stream.py &
```

### **Copy File Baru:**
```powershell
# Di Windows
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
scp backend_server.py entung@10.193.250.211:~/drowsiness-detection/
```

---

## ✅ CHECKLIST SEBELUM BIMBINGAN

- [ ] Raspberry Pi nyala dan connected ke WiFi
- [ ] IP address: 10.193.250.211 (atau cek dengan `hostname -I`)
- [ ] SSH bisa connect dari laptop
- [ ] Backend running (port 5001)
- [ ] Web server running (port 8000)
- [ ] Camera stream running (port 8080)
- [ ] Browser bisa akses aplikasi
- [ ] Webcam laptop bisa digunakan
- [ ] Testing mode berfungsi
- [ ] Export CSV berfungsi

---

## 🎓 PENJELASAN UNTUK DOSEN

### **Konsep:**
Sistem drowsiness detection berbasis web dengan arsitektur hybrid:
- **Frontend** berjalan di browser (laptop)
- **Backend** dan **model inference** di Raspberry Pi (edge computing)
- **Webcam** dari laptop (via WebRTC)

### **Keunggulan:**
- ✅ Portable (edge device)
- ✅ Low latency (~100-200ms)
- ✅ Web-based (cross-platform)
- ✅ Real-time detection
- ✅ Data logging dan export

### **Teknologi:**
- **Backend**: Flask (Python REST API)
- **Model**: MobileNetV2 (TensorFlow/Keras)
- **Frontend**: HTML5, JavaScript, WebRTC
- **Hardware**: Raspberry Pi 5
- **Camera**: Webcam laptop atau Pi Camera

---

## 📖 DOKUMENTASI LENGKAP

File panduan lengkap ada di:
- `DEPLOYMENT_GUIDE.md` - Panduan deployment detail
- `walkthrough.md` - Troubleshooting lengkap

---

**GOOD LUCK BIMBINGAN! 🎉**

---

**Last Updated**: 23 Desember 2025  
**IP Address**: 10.193.250.211  
**Status**: ✅ READY FOR DEMO
