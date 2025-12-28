"""
Convert SavedModel to TFLite di Raspberry Pi
============================================
Jalankan script ini di Raspberry Pi setelah transfer SavedModel
"""

import tensorflow as tf
import os
import zipfile
import hashlib

print("="*60)
print("🔄 Converting SavedModel to TFLite")
print("="*60)
print(f"TensorFlow: {tf.__version__}")
try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
except:
    pass

# Unzip SavedModel
SAVED_MODEL_ZIP = "saved_model_export.zip"
SAVED_MODEL_DIR = "saved_model_export"

if os.path.exists(SAVED_MODEL_ZIP):
    print(f"\n1. Extracting {SAVED_MODEL_ZIP}...")
    with zipfile.ZipFile(SAVED_MODEL_ZIP, 'r') as zip_ref:
        zip_ref.extractall(".")
    print("   ✅ Extracted!")
else:
    print(f"\n❌ File not found: {SAVED_MODEL_ZIP}")
    print("   Transfer file dari Colab dulu!")
    exit(1)

# Convert to TFLite
print(f"\n2. Converting {SAVED_MODEL_DIR} to TFLite...")
converter = tf.lite.TFLiteConverter.from_saved_model(SAVED_MODEL_DIR)

# CRITICAL: Compatibility settings
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS
]
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
tflite_model = converter.convert()
print("   ✅ Converted!")

# Save
OUTPUT = "best_model_raspi.tflite"
with open(OUTPUT, 'wb') as f:
    f.write(tflite_model)

# Test
print(f"\n3. Testing {OUTPUT}...")
try:
    interpreter = tf.lite.Interpreter(model_path=OUTPUT)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print("   ✅ Model loads successfully!")
    print(f"   Input: {input_details[0]['shape']}")
    print(f"   Output: {output_details[0]['shape']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# MD5 check
with open(OUTPUT, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()

print(f"\n4. Verification:")
print(f"   Size: {len(tflite_model)/(1024*1024):.2f} MB")
print(f"   MD5:  {md5}")
print(f"   Old:  7fda967f167768f53531c3477687ed50")

if md5 == "7fda967f167768f53531c3477687ed50":
    print("\n   ❌ WARNING: Same as old file!")
else:
    print("\n   ✅ Different - conversion successful!")

print("\n" + "="*60)
print("✅ SUCCESS!")
print("="*60)
print(f"\nFile created: {OUTPUT}")
print(f"Copy to: cp {OUTPUT} /home/entung/deteksikantuk/backend/best_model_compatible.tflite")
print("="*60)
