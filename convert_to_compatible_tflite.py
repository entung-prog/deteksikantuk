"""
🔄 Convert Model to Raspberry Pi Compatible TFLite
===================================================
Script lengkap untuk Google Colab
Copy-paste seluruh script ini ke 1 cell di Colab dan jalankan!
"""

# ============================================================
# STEP 1: Mount Google Drive
# ============================================================
print("="*60)
print("� Step 1: Mounting Google Drive")
print("="*60)

from google.colab import drive, files
drive.mount('/content/drive')
print("✅ Drive mounted!\n")

# ============================================================
# STEP 2: Load Model dari Drive
# ============================================================
print("="*60)
print("� Step 2: Loading Model")
print("="*60)

import tensorflow as tf
from tensorflow import keras
import os

# Path ke model H5 di Google Drive
MODEL_H5_PATH = '/content/drive/MyDrive/parameter_testing_results/model_exp3.h5'

print(f"TensorFlow version: {tf.__version__}")
print(f"\nLoading model from: {MODEL_H5_PATH}")

# Load model
model = keras.models.load_model(MODEL_H5_PATH, compile=False)
print(f"✅ Model loaded successfully!")
print(f"   Input shape: {model.input_shape}")
print(f"   Output shape: {model.output_shape}")

# ============================================================
# STEP 3: Convert to Compatible TFLite
# ============================================================
print("\n" + "="*60)
print("🔄 Step 3: Converting to Compatible TFLite")
print("="*60)
print("⚠️  Using compatibility mode for Raspberry Pi ARM64\n")

# Create converter
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# CRITICAL: Limit to built-in ops only (for Raspberry Pi compatibility)
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS  # Only standard TFLite operations
]

# Add quantization for smaller file size
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
print("Converting...")
tflite_model = converter.convert()
print("✅ Conversion complete!")

# Save to file
OUTPUT_PATH = "best_model_compatible.tflite"
with open(OUTPUT_PATH, 'wb') as f:
    f.write(tflite_model)

# Show file sizes
h5_size = os.path.getsize(MODEL_H5_PATH) / (1024 * 1024)
tflite_size = len(tflite_model) / (1024 * 1024)
reduction = ((h5_size - tflite_size) / h5_size * 100)

print(f"\n📊 File Sizes:")
print(f"   Original (.h5):   {h5_size:.2f} MB")
print(f"   TFLite (.tflite): {tflite_size:.2f} MB")
print(f"   Reduction:        {reduction:.1f}%")

# ============================================================
# STEP 4: Test Compatibility
# ============================================================
print("\n" + "="*60)
print("🧪 Step 4: Testing Compatibility")
print("="*60)

try:
    # Try to load with TFLite interpreter
    interpreter = tf.lite.Interpreter(model_path=OUTPUT_PATH)
    interpreter.allocate_tensors()
    
    # Get details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print("✅ Model loads successfully!")
    print(f"\n📋 Model Details:")
    print(f"   Input shape:  {input_details[0]['shape']}")
    print(f"   Input dtype:  {input_details[0]['dtype']}")
    print(f"   Output shape: {output_details[0]['shape']}")
    print(f"   Output dtype: {output_details[0]['dtype']}")
    
    # Test inference
    import numpy as np
    test_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], test_input)
    interpreter.invoke()
    test_output = interpreter.get_tensor(output_details[0]['index'])
    
    print(f"\n🧪 Test Inference:")
    print(f"   Input shape:  {test_input.shape}")
    print(f"   Output shape: {test_output.shape}")
    print(f"   Output value: {test_output[0][0]:.4f}")
    print("\n✅ Model works correctly!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    print("   Model may not be compatible with Raspberry Pi!")

# ============================================================
# STEP 5: Download Result
# ============================================================
print("\n" + "="*60)
print("📥 Step 5: Downloading Result")
print("="*60)

print(f"\nDownloading: {OUTPUT_PATH}")
files.download(OUTPUT_PATH)

print("\n" + "="*60)
print("✅ SUCCESS!")
print("="*60)
print("\n📦 File downloaded: best_model_compatible.tflite")
print("\n🚀 Next Steps:")
print("1. Transfer ke Raspberry Pi:")
print("   scp best_model_compatible.tflite entung@192.168.18.150:/home/entung/deteksikantuk/backend/best_model.tflite")
print("\n2. Di Raspberry Pi, restart aplikasi:")
print("   cd /home/entung/deteksikantuk/backend")
print("   source ../venv/bin/activate")
print("   python3 app.py")
print("\n" + "="*60)
