# TensorFlow 2.19 Upgrade Guide

## Overview

Backend telah diupdate untuk mendukung TensorFlow 2.19.0 dengan kompatibilitas penuh untuk Keras 3 dan NumPy 2.0.

## Perubahan Utama

### 1. Dependencies (`requirements.txt`)
- **TensorFlow**: `2.15.0` → `2.19.0`
- **NumPy**: Mendukung NumPy 1.26+ dan 2.0+
- Dependencies lain tetap sama

### 2. Keras 3 Compatibility

TensorFlow 2.19 menggunakan Keras 3 secara default. Semua script konversi sekarang memiliki fallback otomatis:

1. **Coba Keras 3** (default)
2. **Fallback ke Legacy Keras 2** (`TF_USE_LEGACY_KERAS=1`)
3. **Fallback ke tf_keras** (jika terinstall)

### 3. TFLite Interpreter

`app.py` sekarang mencoba import dari 3 lokasi:
1. `tflite_runtime.interpreter` (paling ringan, untuk Raspberry Pi)
2. `tensorflow.lite.python.interpreter` (TF standard)
3. `ai_edge_litert.interpreter` (TF 2.19+ new location)

## Instalasi

### Di Development Machine (Local)

```bash
cd /home/entung/deteksikantuk/backend
pip install -r requirements.txt
```

### Di Raspberry Pi

**Opsi 1: TensorFlow Lite Runtime (Recommended - Lebih Ringan)**
```bash
pip install tflite-runtime
pip install flask flask-cors opencv-python-headless numpy pillow gpiozero picamera2
```

**Opsi 2: Full TensorFlow**
```bash
pip install -r requirements.txt
```

## Testing

### 1. Cek Versi

```bash
python3 -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python3 -c "import numpy as np; print(f'NumPy: {np.__version__}')"
```

Expected output:
```
TensorFlow: 2.19.x
NumPy: 1.26.x atau 2.0.x
```

### 2. Test Model Loading

```bash
cd /home/entung/deteksikantuk/backend
python3 -c "
import tensorflow as tf
interpreter = tf.lite.Interpreter(model_path='best_model_compatible.tflite')
interpreter.allocate_tensors()
print('✅ Model loads successfully')
print(f'Input: {interpreter.get_input_details()[0][\"shape\"]}')
print(f'Output: {interpreter.get_output_details()[0][\"shape\"]}')
"
```

Expected output:
```
✅ Model loads successfully
Input: [  1 224 224   3]
Output: [1 1]
```

### 3. Test Application Startup

```bash
cd /home/entung/deteksikantuk/backend
python3 app.py
```

Expected output harus menampilkan:
```
============================================================
🚗 DROWSINESS DETECTION - SINGLE SERVER
============================================================

📦 Versions:
   TensorFlow: 2.19.x
   NumPy: x.x.x
   OpenCV: 4.8.1

✅ USB Camera initialized at /dev/video8 (640x480 @ 15fps)
✅ Model loaded: /home/entung/deteksikantuk/backend/best_model_compatible.tflite
   Input shape: [  1 224 224   3]
✅ Face cascade loaded from: ...
```

### 4. Test Model Conversion (Jika Ada .h5 Files)

```bash
cd /home/entung/deteksikantuk/backend
python3 convert_model.py best_model.h5 test_output.tflite
```

## Troubleshooting

### Issue: "No module named 'tensorflow'"

**Solusi:**
```bash
pip install tensorflow==2.19.0
```

### Issue: Model loading error dengan Keras 3

**Gejala:**
```
ValueError: Unknown layer: ...
```

**Solusi 1 - Legacy Keras Mode:**
```bash
export TF_USE_LEGACY_KERAS=1
python3 app.py
```

**Solusi 2 - Install tf_keras:**
```bash
pip install tf_keras
```

### Issue: NumPy compatibility warning

**Gejala:**
```
UserWarning: NumPy 2.0 detected...
```

**Solusi:** Ini hanya warning, aplikasi tetap jalan. Untuk menghilangkan warning:
```bash
pip install "numpy<2.0"  # Downgrade ke NumPy 1.26
```
atau
```bash
pip install "numpy>=2.0"  # Upgrade ke NumPy 2.0 stable
```

### Issue: TFLite interpreter deprecation warning

**Gejala:**
```
DeprecationWarning: tf.lite.Interpreter is deprecated...
```

**Solusi:** Ini hanya warning untuk TF 2.20+. Untuk sekarang masih aman digunakan. Tidak perlu action.

### Issue: "No TFLite interpreter found"

**Solusi untuk Raspberry Pi:**
```bash
pip install tflite-runtime
```

## File yang Diupdate

1. ✅ [`requirements.txt`](file:///home/entung/deteksikantuk/backend/requirements.txt) - TensorFlow 2.19.0
2. ✅ [`app.py`](file:///home/entung/deteksikantuk/backend/app.py) - TFLite import chain + version logging
3. ✅ [`convert_h5_to_tflite.py`](file:///home/entung/deteksikantuk/backend/convert_h5_to_tflite.py) - Keras 3 compatibility
4. ✅ [`convert_model.py`](file:///home/entung/deteksikantuk/backend/convert_model.py) - Keras 3 compatibility
5. ✅ [`convert_savedmodel_to_tflite.py`](file:///home/entung/deteksikantuk/backend/convert_savedmodel_to_tflite.py) - Version logging

## Deployment ke Raspberry Pi

### 1. Sync Files

```bash
cd /home/entung/deteksikantuk
./sync_to_raspi.sh
```

atau

```bash
./copy_to_raspi.sh
```

### 2. SSH ke Raspberry Pi

```bash
ssh entung@192.168.18.150
```

**Tip:** Gunakan `tmux` untuk persistent session:
```bash
tmux new -s drowsiness
cd /home/entung/deteksikantuk/backend
python3 app.py

# Detach: Ctrl+B, D
# Reattach: tmux attach -t drowsiness
```

### 3. Install Dependencies

```bash
cd /home/entung/deteksikantuk/backend
pip install -r requirements.txt
```

### 4. Run Application

```bash
python3 app.py
```

### 5. Test di Browser

Buka: `http://192.168.18.150:5000`

## Compatibility Matrix

| Component | TF 2.15 | TF 2.19 | Notes |
|-----------|---------|---------|-------|
| Keras | 2.x | 3.x (default) | Legacy mode available |
| NumPy | 1.24+ | 1.26+ or 2.0+ | Both supported |
| TFLite Interpreter | ✅ | ✅ (deprecated) | Still works |
| Python | 3.9+ | 3.9+ | Same requirement |
| Model Format | .tflite | .tflite | Fully compatible |

## Next Steps

1. ✅ Update dependencies
2. ✅ Update code for compatibility
3. ⏳ Test di local machine
4. ⏳ Deploy ke Raspberry Pi
5. ⏳ Test end-to-end functionality

## References

- [TensorFlow 2.19 Release Notes](https://github.com/tensorflow/tensorflow/releases/tag/v2.19.0)
- [Keras 3 Migration Guide](https://keras.io/guides/migrating_to_keras_3/)
- [NumPy 2.0 Migration Guide](https://numpy.org/devdocs/numpy_2_0_migration_guide.html)
