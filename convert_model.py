"""
Simple Model Converter - Run on Laptop
=======================================
Converts best_model.h5 to TFLite INT8 for Raspberry Pi deployment
"""

import tensorflow as tf
import numpy as np
import os

print("="*60)
print("🔄 SIMPLE MODEL CONVERTER")
print("="*60)

# Load model
print("\n📦 Loading best_model.h5...")
try:
    model = tf.keras.models.load_model('best_model.h5', compile=False)
    print("✅ Model loaded!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 This script must run where model was trained (Google Colab)")
    print("   Or copy this script to Raspberry Pi and run there.")
    exit(1)

print(f"   Input: {model.input_shape}")
print(f"   Output: {model.output_shape}")

# Representative dataset
def representative_dataset():
    print("\n🔢 Generating calibration data...")
    for i in range(100):
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]
        if (i + 1) % 25 == 0:
            print(f"   {i + 1}/100")

# Convert to INT8 TFLite
print("\n🔧 Converting to INT8 TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

tflite_model = converter.convert()

# Save
with open('best_model.tflite', 'wb') as f:
    f.write(tflite_model)

# Stats
h5_size = os.path.getsize('best_model.h5') / 1024 / 1024
tflite_size = len(tflite_model) / 1024 / 1024

print("\n" + "="*60)
print("✅ CONVERSION COMPLETE!")
print("="*60)
print(f"H5 model:     {h5_size:.2f} MB")
print(f"TFLite INT8:  {tflite_size:.2f} MB ({h5_size/tflite_size:.1f}x smaller)")
print("="*60)

print("\n📋 NEXT STEPS:")
print("1. Copy to Raspberry Pi:")
print("   scp best_model.tflite entung@192.168.0.108:~/deteksikantuk/")
print("\n2. On Raspberry Pi:")
print("   cd ~/deteksikantuk")
print("   git pull")
print("   pip install tflite-runtime")
print("   python backend_server.py")
