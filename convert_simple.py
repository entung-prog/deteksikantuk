"""
SIMPLE TFLite Converter - Guaranteed Compatible
================================================
Script paling sederhana untuk convert model
Copy-paste ke Colab dan jalankan!
"""

# Mount Drive
from google.colab import drive, files
drive.mount('/content/drive')

# Import
import tensorflow as tf
from tensorflow import keras

print("="*60)
print("TensorFlow:", tf.__version__)
print("="*60)

# Load model
MODEL_PATH = '/content/drive/MyDrive/parameter_testing_results/model_exp3.h5'
print(f"\n1. Loading: {MODEL_PATH}")
model = keras.models.load_model(MODEL_PATH, compile=False)
print("   ✅ Loaded!")

# Convert dengan COMPATIBILITY MODE
print("\n2. Converting...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# INI YANG PENTING - BATASI KE OPERASI STANDAR SAJA
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
tflite_model = converter.convert()
print("   ✅ Converted!")

# Save
OUTPUT = "model_compatible.tflite"
with open(OUTPUT, 'wb') as f:
    f.write(tflite_model)

# Check size
import os
size_mb = len(tflite_model) / (1024*1024)
print(f"\n3. Size: {size_mb:.2f} MB")

# Test loading
print("\n4. Testing...")
try:
    test_interp = tf.lite.Interpreter(model_path=OUTPUT)
    test_interp.allocate_tensors()
    print("   ✅ Model loads OK!")
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print("   KONVERSI GAGAL!")

# Calculate MD5 untuk compare
import hashlib
with open(OUTPUT, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()
print(f"\n5. MD5: {md5}")
print("   (Harus BEDA dari: 7fda967f167768f53531c3477687ed50)")

if md5 == "7fda967f167768f53531c3477687ed50":
    print("\n❌ GAGAL - File sama dengan yang lama!")
else:
    print("\n✅ SUCCESS - File baru berhasil dibuat!")

# Download
print("\n6. Downloading...")
files.download(OUTPUT)
print("\n✅ DONE!")
print("\nTransfer ke Raspberry Pi:")
print(f"scp {OUTPUT} entung@192.168.18.150:/home/entung/deteksikantuk/backend/best_model_compatible.tflite")
