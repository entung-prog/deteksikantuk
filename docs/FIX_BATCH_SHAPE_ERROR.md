# 🔧 Fix "Unrecognized keyword arguments: batch_shape" Error

## ❌ Error yang Muncul

```
Error loading model: Error when deserializing class 'InputLayer' using config
Exception encountered: Unrecognized keyword arguments: ['batch_shape']
```

---

## 🔍 Penyebab

Model `best_model.h5` di-save dengan versi TensorFlow/Keras yang berbeda dari yang terinstall di Raspberry Pi. Keyword `batch_shape` tidak dikenali oleh versi TensorFlow di Raspi.

---

## ✅ Solusi 1: Load Model dengan Custom Objects (CEPAT!)

Buat file `backend_server_fixed.py`:

```python
"""
Flask Backend Server - Fixed for Keras Compatibility
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras

app = Flask(__name__)
CORS(app)

WEIGHTS_PATH = 'best_model.h5'
IMG_SIZE = (224, 224)

print("="*60)
print("🔄 Loading model with compatibility fix...")
print("="*60)

try:
    # Load model with custom_objects to handle compatibility
    print(f"📦 Loading model from: {WEIGHTS_PATH}")
    
    # Disable eager execution for compatibility
    tf.compat.v1.disable_eager_execution()
    
    # Load with compile=False to avoid optimizer issues
    model = keras.models.load_model(WEIGHTS_PATH, compile=False)
    
    # Recompile with current TensorFlow version
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Model loaded successfully!")
    print(f"   Input shape: {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
    
except Exception as e:
    print(f"❌ ERROR loading model: {e}")
    print("\n💡 Try Solution 2: Rebuild model from scratch")
    model = None

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ... (rest of the code sama seperti backend_server.py)
```

**Jalankan:**
```bash
python backend_server_fixed.py
```

---

## ✅ Solusi 2: Rebuild Model di Raspberry Pi

Karena model incompatible, rebuild model architecture dan load weights saja.

**Buat file `rebuild_model.py`:**

```python
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers
import os

print("Rebuilding model...")

# Build model architecture (sama seperti training)
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

model = tf.keras.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Try to load weights from H5 file
try:
    print("Loading weights from best_model.h5...")
    model.load_weights('best_model.h5', by_name=True, skip_mismatch=True)
    print("✅ Weights loaded!")
    
    # Save as new compatible model
    model.save('best_model_compatible.h5')
    print("✅ Saved as best_model_compatible.h5")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

**Jalankan:**
```bash
python rebuild_model.py
```

**Lalu update backend untuk pakai model baru:**
```python
WEIGHTS_PATH = 'best_model_compatible.h5'
```

---

## ✅ Solusi 3: Re-save Model di Windows dengan Format Kompatibel

**Di Windows (folder webtest):**

Buat file `resave_model_compatible.py`:

```python
import tensorflow as tf
import os

print("Re-saving model in compatible format...")

# Load model
model = tf.keras.models.load_model('best_model.h5')
print("✅ Model loaded")

# Save with SavedModel format (lebih kompatibel)
model.save('best_model_savedmodel', save_format='tf')
print("✅ Saved as SavedModel format")

# Also save as H5 with current TensorFlow version
model.save('best_model_v2.h5')
print("✅ Saved as best_model_v2.h5")

print("\nCopy best_model_v2.h5 to Raspberry Pi:")
print("scp best_model_v2.h5 entung@192.168.0.100:~/deteksikantuk/")
```

**Jalankan:**
```powershell
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
python resave_model_compatible.py
```

**Copy ke Raspi:**
```powershell
scp best_model_v2.h5 entung@192.168.0.100:~/deteksikantuk/
```

**Di Raspi, rename:**
```bash
mv best_model.h5 best_model_old.h5
mv best_model_v2.h5 best_model.h5
```

---

## ✅ Solusi 4: Downgrade/Upgrade TensorFlow di Raspi

Match versi TensorFlow dengan yang digunakan untuk training.

**Cek versi TensorFlow di Windows:**
```powershell
python -c "import tensorflow; print(tensorflow.__version__)"
```

**Install versi yang sama di Raspi:**
```bash
pip uninstall tensorflow
pip install tensorflow==2.15.0  # Ganti dengan versi yang sama
```

---

## 🎯 Rekomendasi (Paling Mudah)

**Solusi 3: Re-save model di Windows**

1. Di Windows: Jalankan `resave_model_compatible.py`
2. Copy `best_model_v2.h5` ke Raspi
3. Rename di Raspi
4. Jalankan backend

Ini paling reliable karena model di-save ulang dengan TensorFlow versi terbaru!

---

## 📊 Troubleshooting

### Masih error setelah re-save?

**Gunakan SavedModel format:**

Di Windows:
```python
model.save('best_model_savedmodel', save_format='tf')
```

Di Raspi, load dengan:
```python
model = tf.keras.models.load_model('best_model_savedmodel')
```

---

**Coba Solusi 3 (re-save di Windows) dulu!** 🚀
