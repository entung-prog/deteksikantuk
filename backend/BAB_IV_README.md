# BAB IV - Dokumentasi File

## 📄 File yang Dibuat

### 1. Dokumen BAB IV
- **File Utama**: `backend/BAB_IV_HASIL_DAN_PEMBAHASAN_FINAL.docx`
- **Status**: ✅ Lengkap dengan semua gambar
- **Ukuran**: ~500 KB (dengan gambar)

### 2. Dokumen Template (tanpa gambar)
- **File**: `backend/BAB_IV_HASIL_DAN_PEMBAHASAN.docx`
- **Status**: Template dengan placeholder gambar
- **Gunakan**: Jika ingin menambahkan gambar manual

## 📸 Gambar yang Digunakan

Semua gambar diambil dari folder `backend/test_results/`:

| No | Gambar | Skenario | Lokasi File |
|----|--------|----------|-------------|
| 4.1 | Normal Driving | Berkendara normal | `normal_driving_20251228_103910.jpg` |
| 4.2 | Simulated Drowsiness | Simulasi kantuk | `simulated_drowsiness_20251228_104027.jpg` |
| 4.3 | Blinking | Kedipan mata | `blinking_20251228_104133.jpg` |
| 4.4 | Low Light | Cahaya rendah | `low_light_20251228_104355.jpg` |
| 4.5 | Bright Light | Cahaya terang | `bright_light_20251228_104500.jpg` |

## 📊 Data Pengujian

Data hasil pengujian tersimpan dalam format CSV di `backend/test_results/`:

- `normal_driving_20251228_103910.csv`
- `simulated_drowsiness_20251228_104027.csv`
- `blinking_20251228_104133.csv`
- `low_light_20251228_104355.csv`
- `bright_light_20251228_104500.csv`

## 🔧 Script yang Dibuat

### 1. `backend/create_bab4.py`
Script untuk membuat dokumen BAB IV dengan struktur lengkap:
- Judul dan sub-bab
- Tabel hasil pengujian
- Analisis dan pembahasan
- Kesimpulan

**Cara menggunakan:**
```bash
python3 backend/create_bab4.py
```

### 2. `backend/insert_images_bab4.py`
Script untuk otomatis memasukkan gambar ke dokumen:
- Mencari placeholder gambar
- Insert gambar dari test_results
- Resize otomatis (5 inches width)

**Cara menggunakan:**
```bash
python3 backend/insert_images_bab4.py
```

## 📋 Struktur Dokumen BAB IV

### BAB IV - HASIL DAN PEMBAHASAN

#### 4.1 Hasil Pengujian Sistem
- 4.1.1 Skenario Pengujian
- 4.1.2 Hasil Pengujian Per Skenario
  - a. Normal Driving
  - b. Simulated Drowsiness
  - c. Blinking
  - d. Low Light
  - e. Bright Light
- 4.1.3 Analisis Performa Sistem
  - a. Perbandingan Hasil Semua Skenario
  - b. Analisis Kecepatan Inferensi
  - c. Analisis Penggunaan Resource

#### 4.2 Pembahasan
- 4.2.1 Akurasi Deteksi Berdasarkan Skenario
- 4.2.2 Performa Real-time
- 4.2.3 Robustness terhadap Kondisi Pencahayaan
- 4.2.4 Efisiensi Penggunaan Resource
- 4.2.5 Keterbatasan Sistem
- 4.2.6 Rekomendasi Perbaikan

#### 4.3 Kesimpulan
- 7 poin kesimpulan utama

## 📊 Ringkasan Hasil Pengujian

| Skenario | Total Frame | Drowsy (%) | Alert (%) | Avg Inference (ms) | CPU (%) |
|----------|-------------|------------|-----------|-------------------|---------|
| Normal Driving | 111 | 48.6 | 51.4 | 172.05 | 56.1 |
| Simulated Drowsiness | 95 | 80.0 | 20.0 | 166.98 | 57.9 |
| Blinking | 83 | 62.7 | 37.3 | 160.16 | 74.4 |
| Low Light | 98 | 88.8 | 11.2 | 130.46 | 58.5 |
| Bright Light | 114 | 69.3 | 30.7 | 135.46 | 68.3 |

## ✅ Checklist

- [x] Dokumen BAB IV dibuat
- [x] Semua tabel hasil pengujian ditambahkan
- [x] 5 gambar hasil test dimasukkan
- [x] Analisis dan pembahasan lengkap
- [x] Kesimpulan dibuat
- [x] Format sesuai dengan BAB III

## 💡 Tips

1. **Membuka Dokumen**: Gunakan Microsoft Word atau LibreOffice Writer
2. **Edit Gambar**: Jika perlu resize, klik gambar dan drag corner
3. **Tambah Gambar Manual**: Insert > Picture > pilih dari test_results
4. **Export PDF**: File > Export as PDF (untuk submission)

## 🎯 File Final yang Digunakan

**Gunakan file ini untuk submission:**
```
backend/BAB_IV_HASIL_DAN_PEMBAHASAN_FINAL.docx
```

File ini sudah lengkap dengan:
- ✅ Semua teks dan tabel
- ✅ Semua 5 gambar hasil test
- ✅ Format yang rapi dan konsisten
- ✅ Siap untuk dicetak atau disubmit
