# Panduan Convert Model di Google Colab

## 🎯 Langkah-Langkah

### 1. Buka Google Colab
- Buka: https://colab.research.google.com
- Klik **New Notebook**

### 2. Upload File ke Colab

#### A. Upload best_model.h5
1. Klik icon **folder** di sidebar kiri
2. Klik tombol **upload** (icon upload)
3. Pilih file `best_model.h5` dari laptop
4. Tunggu upload selesai (~11MB)

#### B. Upload convert_colab.py
1. Klik tombol **upload** lagi
2. Pilih file `convert_colab.py`
3. Tunggu upload selesai

### 3. Jalankan Script di Colab

Di cell pertama, ketik:
```python
!python convert_colab.py
```

Atau copy-paste isi file `convert_colab.py` ke cell dan run.

### 4. Tunggu Proses Selesai

Output yang diharapkan:
```
🔄 H5 TO TFLITE INT8 CONVERTER (GOOGLE COLAB)
TensorFlow version: 2.x.x

📦 STEP 1: Loading best_model.h5...
✅ Model loaded successfully!

🔢 STEP 2: Generating representative dataset (100 samples)...
   Progress: 25/100 samples
   Progress: 50/100 samples
   Progress: 75/100 samples
   Progress: 100/100 samples
✅ Representative dataset ready!

🔧 STEP 3: Converting to INT8 TFLite...
   Converting...
✅ INT8 model saved: best_model.tflite (3.6 MB)

✅ CONVERSION COMPLETE!

📊 Results:
   Original H5:    11.2 MB
   TFLite model:   3.6 MB
   Compression:    3.1x smaller
```

### 5. Download best_model.tflite

1. Klik icon **folder** di sidebar kiri
2. Cari file `best_model.tflite`
3. Klik kanan → **Download**
4. Simpan di laptop

### 6. Copy ke Raspberry Pi

Di laptop (PowerShell):
```powershell
# Ganti path sesuai lokasi download
scp C:\Users\maula\Downloads\best_model.tflite entung@192.168.0.108:~/deteksikantuk/
```

### 7. Di Raspberry Pi

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Masuk ke folder
cd ~/deteksikantuk

# Cek file ada
ls -lh best_model.tflite

# Activate venv
source venv/bin/activate

# Install tflite-runtime
pip install tflite-runtime

# Run backend
python backend_server.py
```

### 8. Test

```bash
# Di terminal lain
curl http://localhost:5001/api/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "TFLite INT8"
}
```

---

## 🔧 Troubleshooting

### Error: "best_model.h5 not found"
- Pastikan file sudah di-upload ke Colab
- Refresh folder view di Colab

### Error saat convert
- Script otomatis fallback ke Float16
- Tetap akan generate `best_model.tflite`

### File tidak muncul setelah convert
- Refresh folder view (klik folder icon 2x)
- Cek di root directory Colab

---

## 📊 Expected Results

| Metric | Value |
|--------|-------|
| Original H5 | ~11 MB |
| TFLite INT8 | ~3.6 MB |
| Compression | 3-4x smaller |
| Accuracy loss | < 1% |
| Speed improvement | 2-3x faster |

---

## ✅ Checklist

- [ ] Buka Google Colab
- [ ] Upload best_model.h5
- [ ] Upload convert_colab.py
- [ ] Run script
- [ ] Download best_model.tflite
- [ ] Copy ke Raspberry Pi
- [ ] Run backend_server.py
- [ ] Test API

---

Selamat mencoba! 🚀
