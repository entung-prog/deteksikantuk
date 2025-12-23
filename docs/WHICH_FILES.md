# 📋 File Mana yang Harus Dipakai?

## 🤖 Backend (Ada 3 File)

### **1. `backend_server.py` ✅ PAKAI INI!**
- **Untuk:** Penggunaan normal
- **Kapan:** Default choice, pakai ini dulu
- **Kelebihan:** Stabil, tested, lengkap
- **Kekurangan:** Butuh RAM cukup (~500MB)

```bash
python backend_server.py
```

---

### **2. `backend_server_optimized.py` ⚡ PAKAI JIKA ERROR**
- **Untuk:** Raspberry Pi dengan RAM terbatas
- **Kapan:** Jika `backend_server.py` error "out of memory"
- **Kelebihan:** Hemat memory, optimized untuk Raspi
- **Kekurangan:** Sedikit lebih lambat

```bash
python backend_server_optimized.py
```

---

### **3. `backend_server_tflite.py` 🧪 EXPERIMENTAL**
- **Untuk:** Jika sudah convert model ke TFLite
- **Kapan:** Hanya jika punya file `best_model.tflite`
- **Kelebihan:** Sangat cepat, hemat memory
- **Kekurangan:** Perlu convert model dulu (ribet)

```bash
python backend_server_tflite.py
```

---

## 📜 JavaScript (Ada 2 File)

### **1. `drowsiness_test_hybrid.js` ✅ PAKAI INI!**
- **Untuk:** Penggunaan dengan backend Python
- **Kapan:** Default choice (sudah di-link di HTML)
- **Kelebihan:** Komunikasi dengan backend via API
- **Fitur:** Real-time detection, logging, export CSV

**Sudah otomatis terpakai di `drowsiness_test.html`!**

---

### **2. `drowsiness_test.js` 🔧 ALTERNATIF**
- **Untuk:** Standalone (tanpa backend)
- **Kapan:** Jika ingin pakai TensorFlow.js di browser
- **Kelebihan:** Tidak perlu backend Python
- **Kekurangan:** Perlu convert model ke TFJS, lebih lambat

**Tidak dipakai secara default.**

---

## 🎯 Rekomendasi Penggunaan

### **Scenario 1: Normal (Raspberry Pi dengan RAM cukup)**
```bash
# Backend
python backend_server.py

# Web Server (terminal baru)
python3 -m http.server 8000

# JS yang dipakai
drowsiness_test_hybrid.js (otomatis)
```

---

### **Scenario 2: Raspberry Pi RAM Terbatas / Error Memory**
```bash
# 1. Increase swap dulu!
sudo nano /etc/dphys-swapfile
# Ubah CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 2. Pakai backend optimized
python backend_server_optimized.py

# 3. Web Server (terminal baru)
python3 -m http.server 8000

# JS yang dipakai
drowsiness_test_hybrid.js (otomatis)
```

---

### **Scenario 3: Experimental (TFLite)**
```bash
# 1. Convert model dulu (di Windows)
python convert_to_tflite.py

# 2. Copy ke Raspi
scp best_model.tflite entung@192.168.0.108:~/deteksikantuk/

# 3. Install TFLite runtime
pip install tflite-runtime

# 4. Pakai backend TFLite
python backend_server_tflite.py

# 5. Web Server (terminal baru)
python3 -m http.server 8000

# JS yang dipakai
drowsiness_test_hybrid.js (otomatis)
```

---

## ✅ Kesimpulan Singkat

| File | Pakai? | Kapan? |
|------|--------|--------|
| **backend_server.py** | ✅ **YA** | Default, mulai dari ini |
| **backend_server_optimized.py** | ⚡ Jika perlu | Error memory / Raspi lemah |
| **backend_server_tflite.py** | 🧪 Experimental | Sudah punya TFLite model |
| **drowsiness_test_hybrid.js** | ✅ **YA** | Otomatis terpakai |
| **drowsiness_test.js** | ❌ Tidak | Alternatif standalone |

---

## 🚀 Quick Start (Paling Mudah)

```bash
# 1. Jalankan backend default
python backend_server.py

# 2. Jalankan web server (terminal baru)
python3 -m http.server 8000

# 3. Akses dari browser
# http://192.168.0.108:8000/drowsiness_test.html

# JS otomatis pakai: drowsiness_test_hybrid.js
```

**Selesai!** Tidak perlu ubah apapun, semuanya sudah di-setup! ✅

---

## 🔧 Troubleshooting

### Backend error "out of memory"?
→ Pakai `backend_server_optimized.py` atau increase swap

### Ingin lebih cepat?
→ Convert ke TFLite dan pakai `backend_server_tflite.py`

### JS tidak jalan?
→ Cek di browser console (F12), seharusnya pakai `drowsiness_test_hybrid.js`

---

**Rekomendasi: Pakai `backend_server.py` + `drowsiness_test_hybrid.js` (default)!** 🎯
