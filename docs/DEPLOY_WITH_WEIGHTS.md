# Deployment dengan Model Weights

## 📦 Files yang Dibutuhkan

Copy file-file ini ke Raspberry Pi:
- `model_weights.weights.h5` (weights file)
- `backend_server_weights.py` (backend server)
- `drowsiness_test.html` (frontend)
- `drowsiness_test_hybrid.js` (frontend JS)

## 🚀 Langkah Deploy

### 1. Copy ke Raspberry Pi

```powershell
# Dari laptop Windows
scp model_weights.weights.h5 entung@192.168.0.108:~/deteksikantuk/
scp backend_server_weights.py entung@192.168.0.108:~/deteksikantuk/
```

### 2. Setup di Raspberry Pi

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Masuk ke folder
cd ~/deteksikantuk

# Activate virtual environment
source venv/bin/activate

# Install dependencies (jika belum)
pip install flask flask-cors opencv-python-headless tensorflow
```

### 3. Jalankan Backend

```bash
python backend_server_weights.py
```

Expected output:
```
🏗️  Building model architecture...
✅ Architecture built!
   Input shape: (None, 224, 224, 3)
   Output shape: (None, 4)

📦 Loading weights from model_weights.weights.h5...
✅ Weights loaded successfully!

🚀 DROWSINESS DETECTION BACKEND SERVER
Server running on: http://0.0.0.0:5001
```

### 4. Test API

```bash
# Di terminal lain
curl http://localhost:5001/api/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "Keras (from weights)",
  "weights_file": "model_weights.weights.h5"
}
```

## ✅ Keuntungan Metode Ini

- ✅ **No batch_shape error** - Rebuild architecture fresh
- ✅ **Simple** - Tidak perlu convert
- ✅ **Works anywhere** - Laptop atau Raspberry Pi
- ✅ **Same accuracy** - Pakai weights yang sama

## ⚠️ Kekurangan

- ❌ **Lebih lambat** - Tidak ada quantization optimization
- ❌ **File lebih besar** - ~14MB vs ~3.6MB (INT8)
- ❌ **Lebih berat** - Butuh full TensorFlow

## 💡 Rekomendasi

**Untuk development/testing:** Pakai metode ini (simple!)

**Untuk production/deployment:** Convert ke INT8 TFLite (lebih cepat & ringan)

## 🔄 Jika Mau Convert Nanti

Jalankan script ini kapan saja:
```bash
python convert_weights_to_tflite.py
```

Akan generate:
- `best_model_int8.tflite` (4x lebih kecil, 2-3x lebih cepat)
- `best_model_float16.tflite` (2x lebih kecil)
