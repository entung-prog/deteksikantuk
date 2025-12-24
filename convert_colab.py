"""
Convert H5 Model to TFLite INT8 - Google Colab Version
======================================================
Upload best_model.h5 to Colab, run this script, download best_model.tflite

Instructions:
1. Upload best_model.h5 to Colab
2. Run this entire notebook
3. Download best_model.tflite
4. Copy to Raspberry Pi
"""

import tensorflow as tf
import numpy as np
import os

print("="*70)
print("🔄 H5 TO TFLITE INT8 CONVERTER (GOOGLE COLAB)")
print("="*70)
print(f"TensorFlow version: {tf.__version__}")
print("="*70)

# ============================================================
# STEP 1: LOAD MODEL
# ============================================================

print("\n📦 STEP 1: Loading best_model.h5...")

# Check if file exists
if not os.path.exists('best_model.h5'):
    print("❌ ERROR: best_model.h5 not found!")
    print("\n💡 Please upload best_model.h5 to Colab:")
    print("   1. Click folder icon on left sidebar")
    print("   2. Click upload button")
    print("   3. Select best_model.h5")
    print("   4. Wait for upload to complete")
    print("   5. Run this script again")
    raise FileNotFoundError("best_model.h5 not found")

try:
    model = tf.keras.models.load_model('best_model.h5', compile=False)
    print("✅ Model loaded successfully!")
    print(f"   Input shape:  {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
    print(f"   Total params: {model.count_params():,}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    raise

# ============================================================
# STEP 2: REPRESENTATIVE DATASET
# ============================================================

def representative_dataset():
    """
    Generate representative dataset for INT8 quantization.
    This helps the converter determine optimal quantization parameters.
    """
    print("\n🔢 STEP 2: Generating representative dataset (100 samples)...")
    for i in range(100):
        # Generate random data matching model input (224x224x3)
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]
        if (i + 1) % 25 == 0:
            print(f"   Progress: {i + 1}/100 samples")
    print("✅ Representative dataset ready!")

# ============================================================
# STEP 3: CONVERT TO INT8 TFLITE
# ============================================================

print("\n🔧 STEP 3: Converting to INT8 TFLite...")
print("   This may take 1-2 minutes...")

try:
    # Create converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Enable INT8 quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    
    # Full integer quantization
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8
    
    # Convert
    print("   Converting...")
    tflite_int8 = converter.convert()
    
    # Save
    with open('best_model.tflite', 'wb') as f:
        f.write(tflite_int8)
    
    int8_size = len(tflite_int8) / 1024 / 1024
    print(f"✅ INT8 model saved: best_model.tflite ({int8_size:.2f} MB)")
    
except Exception as e:
    print(f"❌ INT8 conversion failed: {e}")
    print("\nTrying Float16 quantization instead...")
    
    try:
        # Fallback to Float16
        converter2 = tf.lite.TFLiteConverter.from_keras_model(model)
        converter2.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_float16 = converter2.convert()
        
        with open('best_model.tflite', 'wb') as f:
            f.write(tflite_float16)
        
        float16_size = len(tflite_float16) / 1024 / 1024
        print(f"✅ Float16 model saved: best_model.tflite ({float16_size:.2f} MB)")
        tflite_int8 = tflite_float16
        
    except Exception as e2:
        print(f"❌ All conversions failed: {e2}")
        raise

# ============================================================
# STEP 4: SUMMARY
# ============================================================

print("\n" + "="*70)
print("✅ CONVERSION COMPLETE!")
print("="*70)

h5_size = os.path.getsize('best_model.h5') / 1024 / 1024
tflite_size = len(tflite_int8) / 1024 / 1024

print(f"\n📊 Results:")
print(f"   Original H5:    {h5_size:.2f} MB")
print(f"   TFLite model:   {tflite_size:.2f} MB")
print(f"   Compression:    {h5_size/tflite_size:.1f}x smaller")
print(f"   Size reduction: {(1 - tflite_size/h5_size) * 100:.1f}%")

print("\n" + "="*70)
print("📥 DOWNLOAD INSTRUCTIONS")
print("="*70)

print("\n1️⃣  Download best_model.tflite from Colab:")
print("   - Click folder icon on left sidebar")
print("   - Right-click on 'best_model.tflite'")
print("   - Select 'Download'")

print("\n2️⃣  Copy to Raspberry Pi:")
print("   From your laptop (PowerShell):")
print("   scp best_model.tflite entung@192.168.0.108:~/deteksikantuk/")

print("\n3️⃣  On Raspberry Pi:")
print("   cd ~/deteksikantuk")
print("   source venv/bin/activate")
print("   pip install tflite-runtime")
print("   python backend_server.py")

print("\n4️⃣  Test:")
print("   curl http://localhost:5001/api/health")

print("\n" + "="*70)
print("✨ All done! Your model is ready for deployment!")
print("="*70)

# Verify file was created
if os.path.exists('best_model.tflite'):
    print(f"\n✅ File verified: best_model.tflite ({os.path.getsize('best_model.tflite') / 1024 / 1024:.2f} MB)")
else:
    print("\n❌ Warning: best_model.tflite not found!")
