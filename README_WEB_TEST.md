# Drowsiness Detection - Web Testing Interface

## 📋 Deskripsi

Interface web untuk testing model drowsiness detection dengan fitur:
- ✅ Real-time webcam capture dengan visualisasi
- ✅ Mode Testing untuk capture otomatis dan logging hasil
- ✅ Mode Visualisasi untuk demo real-time
- ✅ FPS Counter untuk monitoring performa
- ✅ Tabel hasil pengujian yang dapat di-export ke CSV
- ✅ Alarm otomatis saat terdeteksi mengantuk

## 🚀 Cara Penggunaan

### 1. Convert Model ke TensorFlow.js

Pertama, install dependency yang diperlukan:

```powershell
pip install tensorflowjs
```

Kemudian convert model H5 ke TensorFlow.js format:

```powershell
# Float32 (akurasi maksimal, ~23MB)
python convert_model_to_tfjs.py --input best_model.h5 --output model_tfjs

# ATAU INT8 Quantized (ukuran lebih kecil, ~6MB)
python convert_model_to_tfjs.py --input best_model.h5 --output model_tfjs --quantize
```

Setelah selesai, akan ada folder `model_tfjs/` berisi:
- `model.json` - Model architecture
- `group1-shard*.bin` - Model weights

### 2. Jalankan Local Server

**PENTING:** Web interface harus dijalankan melalui local server (tidak bisa dibuka langsung dengan double-click HTML file) karena:
- CORS policy untuk loading model
- Webcam access memerlukan HTTPS atau localhost

Jalankan local server dengan Python:

```powershell
# Python 3
python -m http.server 8000

# Atau jika ada konflik port
python -m http.server 8080
```

### 3. Buka di Browser

Buka browser (Chrome/Edge recommended) dan akses:

```
http://localhost:8000/drowsiness_test.html
```

Browser akan meminta permission untuk mengakses webcam - klik **Allow**.

## 🎮 Fitur-Fitur

### Mode Visualisasi

1. Klik tombol **"Start Visualization"**
2. Interface akan menampilkan:
   - Face detection box (biru)
   - Eye region boxes (hijau)
   - Status real-time (Alert/Drowsy)
   - Confidence percentage
   - FPS counter
3. Klik **"Stop Visualization"** untuk berhenti

### Mode Testing

1. Klik tombol **"Start Testing Mode"**
2. Sistem akan:
   - Auto-capture setiap N detik (default: 2 detik)
   - Mencatat hasil ke tabel: timestamp, status, confidence, duration
   - Menghitung statistik (alert count, drowsy count, avg confidence)
3. Klik **"Stop Testing Mode"** untuk berhenti
4. Klik **"Export CSV"** untuk download hasil testing

### Settings

- **Drowsy Threshold** (0.1 - 0.9): Batas confidence untuk menentukan drowsy/alert
  - Default: 0.5
  - Nilai lebih tinggi = lebih sensitif (lebih mudah terdeteksi drowsy)
  
- **Alarm Duration** (1-10 detik): Durasi drowsy sebelum alarm muncul
  - Default: 3 detik
  - Jika mata tertutup selama durasi ini → alarm muncul
  
- **Capture Interval** (1-10 detik): Interval capture di testing mode
  - Default: 2 detik
  - Interval lebih kecil = data lebih banyak

## 📊 Cara Membuat Laporan

### Metode 1: Export CSV

1. Jalankan testing mode selama beberapa menit
2. Lakukan berbagai skenario:
   - Mata terbuka (alert)
   - Mata tertutup sebentar
   - Mata tertutup lama (drowsy)
3. Klik **"Export CSV"**
4. Buka file CSV di Excel/Google Sheets
5. Buat grafik/analisis dari data

### Metode 2: Screenshot Tabel

1. Setelah testing selesai
2. Screenshot tabel hasil
3. Paste ke laporan

### Contoh Skenario Testing

**Skenario 1: Normal Driving**
- Durasi: 2 menit
- Kondisi: Mata terbuka normal
- Expected: Mayoritas "Alert"

**Skenario 2: Drowsy Simulation**
- Durasi: 2 menit
- Kondisi: Tutup mata setiap 10 detik selama 3-5 detik
- Expected: Beberapa "Drowsy" terdeteksi, alarm muncul

**Skenario 3: Mixed**
- Durasi: 5 menit
- Kondisi: Kombinasi alert dan drowsy
- Expected: Data bervariasi

## 🔧 Troubleshooting

### Model tidak load

**Error:** `Failed to load model.json`

**Solusi:**
1. Pastikan folder `model_tfjs/` ada di direktori yang sama dengan HTML
2. Pastikan menjalankan via local server (bukan double-click HTML)
3. Check console browser (F12) untuk error detail

### Webcam tidak muncul

**Error:** `Cannot access webcam`

**Solusi:**
1. Pastikan browser meminta permission dan Anda klik "Allow"
2. Pastikan tidak ada aplikasi lain yang menggunakan webcam
3. Coba browser lain (Chrome/Edge recommended)
4. Pastikan mengakses via `localhost` (bukan `file://`)

### FPS rendah (< 10)

**Penyebab:**
- Komputer kurang powerful
- Model terlalu besar

**Solusi:**
1. Convert model dengan INT8 quantization (lebih ringan)
2. Kurangi resolusi webcam di code (edit `getUserMedia` width/height)
3. Gunakan browser yang lebih ringan

### Face tidak terdeteksi

**Penyebab:**
- Pencahayaan kurang
- Wajah terlalu jauh/dekat
- Sudut kamera tidak tepat

**Solusi:**
1. Pastikan pencahayaan cukup
2. Posisikan wajah di tengah frame
3. Jarak ideal: 50-100cm dari kamera

## 📁 File Structure

```
pipeline/
├── drowsiness_test.html          # Main HTML interface
├── drowsiness_test.css           # Styling
├── drowsiness_test.js            # JavaScript logic
├── convert_model_to_tfjs.py      # Model converter
├── best_model.h5                 # Original H5 model
└── model_tfjs/                   # Converted model (after conversion)
    ├── model.json
    └── group1-shard*.bin
```

## 🌐 Browser Compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome | ✅ Recommended | Best performance |
| Edge | ✅ Recommended | Best performance |
| Firefox | ⚠️ Works | Slightly slower |
| Safari | ❌ Not tested | May have issues with TensorFlow.js |

## 💡 Tips

1. **Untuk Laporan:**
   - Lakukan minimal 3 skenario testing berbeda
   - Capture minimal 50-100 data points per skenario
   - Screenshot interface saat alarm muncul
   - Export CSV dan buat grafik di Excel

2. **Untuk Performa Optimal:**
   - Gunakan Chrome/Edge
   - Tutup aplikasi lain yang berat
   - Pastikan pencahayaan cukup
   - Gunakan INT8 model jika FPS < 15

3. **Untuk Akurasi:**
   - Kalibrasi threshold sesuai kondisi
   - Test di berbagai kondisi pencahayaan
   - Test dengan berbagai jarak kamera

## 📞 Support

Jika ada masalah, check:
1. Browser console (F12) untuk error messages
2. Network tab untuk model loading issues
3. Pastikan semua file ada di direktori yang benar

---

**Selamat Testing! 🚀**
