# 📊 Script Generate Analisis Hasil Pengujian

## 📁 File yang Tersedia

### 1. `generate_analysis.py` - Script Python Utama
Script Python untuk membaca semua file CSV di folder `test_results/` dan generate analisis lengkap.

**Fitur**:
- ✅ Membaca semua file CSV secara otomatis
- ✅ Parse data: total samples, drowsy/alert count, inference time, resource usage
- ✅ Menghitung FPS dari inference time
- ✅ Generate analisis per skenario
- ✅ Membuat tabel ringkasan
- ✅ Memberikan rekomendasi perbaikan
- ✅ Output: `test_results/ANALISIS_HASIL.md`

### 2. `run_analysis.sh` - Bash Script Wrapper
Script bash untuk menjalankan analisis dan menampilkan summary.

**Fitur**:
- ✅ Menjalankan `generate_analysis.py`
- ✅ Menampilkan quick summary
- ✅ Preview 30 baris pertama hasil analisis

---

## 🚀 Cara Menggunakan

### Opsi 1: Python Script (Recommended)
```bash
cd /home/entung/deteksikantuk/backend
python3 generate_analysis.py
```

**Output**:
```
============================================================
📊 GENERATE ANALISIS HASIL PENGUJIAN
============================================================

📊 Found 5 CSV files
   Reading: blinking_20251228_020118.csv
   Reading: bright_light_20251228_020027.csv
   Reading: low_light_20251228_015929.csv
   Reading: normal_driving_20251228_015735.csv
   Reading: simulated_drowsiness_20251228_015841.csv

✅ Analisis berhasil dibuat: test_results/ANALISIS_HASIL.md
📊 Total 5 skenario dianalisis

============================================================
✅ SELESAI!
============================================================
```

### Opsi 2: Bash Script (dengan Preview)
```bash
cd /home/entung/deteksikantuk/backend
./run_analysis.sh
```

**Output**: Sama seperti opsi 1 + preview 30 baris pertama

---

## 📋 Format Input (CSV)

Script membaca CSV dengan format:
```csv
# Test Results Export
# Scenario,normal_driving
# Timestamp,2025-12-28 01:57:35
# Duration,33.3 seconds

Summary Statistics
Metric,Value
Total Detections,105
Drowsy Detected,17
Alert Detected,88
Avg Inference Time (ms),172.86

Resource Usage
Resource,Value
CPU Usage (%),59.0
RAM Usage (GB),1.93

Inference Times (ms)
Sample,Time (ms)
1,234.72
2,280.8
...
```

---

## 📊 Format Output (Markdown)

File `ANALISIS_HASIL.md` berisi:

1. **Header**: Tanggal dan waktu generate
2. **Tabel Ringkasan**: Semua skenario dalam satu tabel
3. **Analisis Per Skenario**: Detail setiap skenario dengan:
   - Hasil (total, drowsy, alert, inference, CPU, RAM)
   - Analisis otomatis (baik/buruk/cukup)
   - Persentase akurasi
4. **Performa Sistem**:
   - Tabel inference time & FPS
   - Tabel resource usage (min/max/avg)
5. **Kesimpulan**:
   - Kekuatan sistem
   - Kelemahan sistem
   - Rekomendasi perbaikan

---

## 🎯 Contoh Analisis Otomatis

Script akan otomatis memberikan analisis berdasarkan skenario:

### Normal Driving
- Jika Alert > 80%: ✅ BAIK
- Jika Alert < 80%: ⚠️ PERHATIAN
- Jika Drowsy > 20%: ⚠️ False Positive tinggi

### Simulated Drowsiness
- Jika Drowsy > 70%: ✅ BAIK
- Jika Drowsy 40-70%: ⚠️ CUKUP
- Jika Drowsy < 40%: ❌ KURANG (False Negative tinggi)

### Blinking
- Jika Alert > 90%: ✅ SANGAT BAIK
- Jika Alert 70-90%: ⚠️ CUKUP
- Jika Alert < 70%: ❌ BURUK (False Positive tinggi)

### Low Light
- Jika Drowsy > 60%: ⚠️ OVER-DETECTION
- Jika seimbang: ✅ BAIK

### Bright Light
- Jika Alert > 90%: ✅ SANGAT BAIK
- Jika Alert < 90%: ⚠️ CUKUP

---

## 🔄 Workflow Penggunaan

### 1. Setelah Pengujian
```bash
# Setelah export semua skenario dari web interface
cd /home/entung/deteksikantuk/backend
python3 generate_analysis.py
```

### 2. Review Hasil
```bash
# Buka file analisis
cat test_results/ANALISIS_HASIL.md

# Atau buka dengan editor
nano test_results/ANALISIS_HASIL.md
```

### 3. Update Dokumentasi Bab 4
- Copy tabel ringkasan ke dokumen Bab 4
- Copy analisis per skenario
- Copy kesimpulan dan rekomendasi

---

## 📝 Customization

### Mengubah Threshold Analisis

Edit `generate_analysis.py`, cari bagian:

```python
if 'normal' in data['scenario'].lower():
    if alert_pct > 80:  # ← Ubah threshold di sini
        f.write(f"- ✅ **BAIK**: ...")
```

### Menambah Metrik Baru

1. Tambahkan parsing di fungsi `parse_csv()`
2. Tambahkan ke tabel di fungsi `generate_analysis()`
3. Tambahkan analisis di bagian per-skenario

---

## 🐛 Troubleshooting

### Error: "No CSV files found"
**Solusi**: Pastikan ada file CSV di folder `test_results/`

### Error: "Permission denied"
**Solusi**: 
```bash
chmod +x run_analysis.sh
```

### Output tidak lengkap
**Solusi**: Pastikan format CSV sesuai (ada header metadata dan summary statistics)

---

## 💡 Tips

1. **Jalankan setelah semua skenario selesai** untuk analisis lengkap
2. **Simpan file lama** sebelum generate ulang (akan overwrite)
3. **Gunakan untuk dokumentasi Bab 4** - copy paste langsung ke dokumen
4. **Re-run kapan saja** jika ada CSV baru ditambahkan

---

## 📚 File Terkait

- `generate_analysis.py` - Script Python utama
- `run_analysis.sh` - Bash wrapper
- `test_results/` - Folder berisi CSV dan hasil analisis
- `testing_guide.md` - Panduan pengujian
- `FITUR_LENGKAP.md` - Dokumentasi fitur

---

**Dibuat**: 28 Desember 2025  
**Update Terakhir**: 28 Desember 2025
