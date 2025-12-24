# Model Quantization Guide: INT8 & INT4 TFLite

## 🎯 Overview

Panduan lengkap untuk mengkonversi model drowsiness detection dari H5 ke TFLite dengan quantization INT8/INT4.

## ❌ Problem: batch_shape Error

Error yang Anda alami:
```
TypeError: Error when deserializing class 'InputLayer'
Exception encountered: Unrecognized keyword arguments: ['batch_shape']
```

**Penyebab:** Model `best_model.h5` dibuat dengan versi Keras yang berbeda dari environment Raspberry Pi.

**Solusi:** Konversi model di environment yang sama dengan tempat training (Google Colab).

---

## 📊 Perbandingan Quantization

| Format | Size | Speed | Accuracy | Use Case |
|--------|------|-------|----------|----------|
| **Original H5** | 100% | Baseline | 100% | Development |
| **INT8 TFLite** | ~25% (4x smaller) | 2-3x faster | ~99% | **Raspberry Pi** ⭐ |
| **INT4 TFLite** | ~12.5% (8x smaller) | 3-4x faster | ~95-98% | Very constrained devices |
| **Float16 TFLite** | ~50% (2x smaller) | 1.5x faster | ~99.9% | Fallback option |

### Rekomendasi:
- **INT8**: Best choice untuk Raspberry Pi (balance optimal)
- **INT4**: Hanya jika size sangat critical (accuracy loss lebih besar)
- **Float16**: Fallback jika INT8 bermasalah

---

## 🚀 Langkah-Langkah Konversi

### Step 1: Upload ke Google Colab

1. Buka Google Colab: https://colab.research.google.com
2. Upload file:
   - `best_model.h5` (model original)
   - `convert_to_tflite_colab.py` (script converter)

### Step 2: Jalankan Script di Colab

```python
# Di Google Colab
!python convert_to_tflite_colab.py
```

Script akan generate:
- ✅ `best_model_int8.tflite` - INT8 quantized (RECOMMENDED)
- ✅ `best_model_float16.tflite` - Float16 quantized
- ✅ `best_model_standard.tflite` - No quantization
- ✅ `best_model_fixed.h5` - Compatible H5 format

### Step 3: Download dari Colab

Klik kanan pada file → Download:
- `best_model_int8.tflite` (prioritas utama)
- `best_model_float16.tflite` (backup)

### Step 4: Copy ke Raspberry Pi

```bash
# Dari laptop Windows (PowerShell)
scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/

# Rename sebagai model utama
scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/best_model.tflite
```

### Step 5: Install TFLite Runtime di Raspberry Pi

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Activate virtual environment
cd ~/deteksikantuk
source venv/bin/activate

# Install tflite-runtime (lebih ringan dari TensorFlow!)
pip install tflite-runtime
```

### Step 6: Update Backend Server

File `backend_server_tflite.py` sudah siap! Cek konfigurasi:

```python
# Pastikan MODEL_PATH mengarah ke file TFLite
MODEL_PATH = 'best_model.tflite'  # atau 'best_model_int8.tflite'
```

### Step 7: Test Backend

```bash
# Jalankan backend dengan TFLite
python backend_server_tflite.py

# Di terminal lain, test API
curl http://localhost:5001/api/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "TensorFlow Lite"
}
```

---

## 🔧 Troubleshooting

### Error: "No module named 'tflite_runtime'"

```bash
pip install tflite-runtime
```

### Error: "Failed to load model"

Check file exists:
```bash
ls -lh ~/deteksikantuk/*.tflite
```

### Model loaded but predictions wrong

Cek input/output type:
```python
# Di backend_server_tflite.py, line 103-110
# Script sudah handle INT8 (uint8) dan Float32 otomatis
```

### Performance masih lambat

1. Pastikan menggunakan `tflite-runtime`, bukan `tensorflow`
2. Gunakan INT8 model (bukan Float16)
3. Check CPU usage: `htop`

---

## 📈 Expected Results

### File Sizes (example)
```
best_model.h5           : 14.2 MB
best_model_int8.tflite  : 3.6 MB  (4x smaller) ⭐
best_model_float16.tflite: 7.1 MB  (2x smaller)
```

### Inference Speed (Raspberry Pi 4)
```
H5 model:        ~150-200ms per frame
INT8 TFLite:     ~50-70ms per frame   (3x faster) ⭐
Float16 TFLite:  ~80-100ms per frame  (2x faster)
```

### Accuracy
```
Original:   95.2%
INT8:       94.8% (loss: 0.4%)  ✅ Acceptable
Float16:    95.1% (loss: 0.1%)
```

---

## 🎓 Technical Details

### INT8 Quantization Process

1. **Calibration**: Menggunakan representative dataset (100 samples)
2. **Weight Quantization**: Float32 → INT8 (256 values)
3. **Activation Quantization**: Float32 → UINT8 (0-255)
4. **Scale/Zero-point**: Menyimpan parameters untuk dequantization

### Formula
```
real_value = scale * (quantized_value - zero_point)
```

### Backend Handling

`backend_server_tflite.py` otomatis detect dan handle:
- ✅ INT8 quantized models (uint8 input/output)
- ✅ Float32 models (float32 input/output)
- ✅ Mixed precision models

---

## 📝 Files Created

| File | Purpose | Location |
|------|---------|----------|
| `convert_to_tflite_colab.py` | Conversion script | Run in Google Colab |
| `backend_server_tflite.py` | TFLite backend | Raspberry Pi |
| `best_model_int8.tflite` | INT8 model | Raspberry Pi |
| `best_model_float16.tflite` | Float16 model | Backup |

---

## ✅ Quick Start Summary

```bash
# 1. Di Google Colab
!python convert_to_tflite_colab.py
# Download: best_model_int8.tflite

# 2. Di Laptop (PowerShell)
scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/best_model.tflite

# 3. Di Raspberry Pi
ssh entung@192.168.0.108
cd ~/deteksikantuk
source venv/bin/activate
pip install tflite-runtime
python backend_server_tflite.py

# 4. Test
curl http://localhost:5001/api/health
```

---

## 🎯 Next Steps

1. ✅ Convert model di Google Colab
2. ✅ Deploy ke Raspberry Pi
3. ⏭️ Test inference speed
4. ⏭️ Compare accuracy dengan H5 model
5. ⏭️ Optimize threshold jika perlu

---

## 💡 Tips

- **Always use INT8 for Raspberry Pi** - Best balance
- **Keep Float16 as backup** - Jika INT8 bermasalah
- **Monitor CPU usage** - INT8 should use less CPU
- **Test accuracy** - Compare dengan H5 model
- **Use tflite-runtime** - Jangan install full TensorFlow

---

## 📞 Support

Jika ada masalah:
1. Check error message di terminal
2. Verify file sizes (INT8 should be ~4x smaller)
3. Test dengan `curl` untuk isolate masalah
4. Check TensorFlow version compatibility
