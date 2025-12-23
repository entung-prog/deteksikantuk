# Quick Start Guide - Hybrid Version

## 🚀 Cara Menjalankan

### Step 1: Start Backend Server

Buka terminal baru dan jalankan:

```powershell
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\web_test
python backend_server.py
```

Server akan running di `http://localhost:5000`

### Step 2: Start Web Server

Terminal sudah running di port 8000 (jangan ditutup!)

Jika belum, jalankan:

```powershell
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\web_test
python -m http.server 8000
```

### Step 3: Buka Browser

Buka browser dan akses:

```
http://localhost:8000/drowsiness_test.html
```

### Step 4: Test!

1. Allow webcam access
2. Click "Start Visualization" → lihat deteksi real-time
3. Click "Start Testing Mode" → mulai logging otomatis
4. Coba tutup mata 3+ detik → alarm akan muncul
5. Click "Export CSV" → download hasil testing

## 📁 File Structure

```
web_test/
├── backend_server.py              # Flask backend (port 5000)
├── drowsiness_test.html           # Web interface
├── drowsiness_test.css            # Styling
├── drowsiness_test_hybrid.js      # JavaScript (hybrid version)
└── README_WEB_TEST.md             # Full documentation
```

## ⚙️ How It Works

1. **Web UI** (JavaScript) captures webcam frames
2. **Sends** frames to Flask backend via HTTP POST
3. **Backend** (Python) runs model inference with H5 model
4. **Returns** prediction results (confidence, is_drowsy, face_box)
5. **Web UI** displays results and logs data

## 💡 Advantages

✅ Uses existing H5 model directly (no conversion needed!)
✅ Full Python TensorFlow support
✅ Modern web interface for testing
✅ Easy to modify backend logic
✅ CSV export for reports

## 🔧 Troubleshooting

**Backend won't start:**
- Make sure Flask is installed: `pip install flask flask-cors`
- Check if port 5000 is available

**Web UI shows "Backend Error":**
- Make sure backend server is running
- Check console (F12) for CORS errors

**Low FPS:**
- Normal! Backend processing takes time
- Expected: 5-15 FPS (vs 30+ FPS with TensorFlow.js)
- Still good enough for testing

---

**Ready to test! 🎉**
