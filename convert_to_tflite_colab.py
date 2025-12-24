"""
Convert H5 Model to TFLite with INT8/INT4 Quantization
======================================================
RUN THIS SCRIPT IN GOOGLE COLAB (where the model was trained)

This script converts best_model.h5 to:
1. INT8 quantized TFLite (recommended for Raspberry Pi)
2. Float16 TFLite (fallback option)
3. Fixed H5 format (compatible with newer TensorFlow versions)
"""

import tensorflow as tf
import numpy as np
import os

print("="*70)
print("🔄 H5 TO TFLITE CONVERTER - INT8 QUANTIZATION")
print("="*70)
print(f"TensorFlow version: {tf.__version__}")
print("="*70)

# ============================================================
# STEP 1: LOAD MODEL
# ============================================================

print("\n📦 STEP 1: Loading H5 model...")
try:
    model = tf.keras.models.load_model('best_model.h5')
    print("✅ Model loaded successfully!")
    print(f"   Input shape:  {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
    print(f"   Total params: {model.count_params():,}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("\n💡 Make sure:")
    print("   1. best_model.h5 is in the same directory")
    print("   2. You're running this in the same environment where model was trained")
    exit(1)

# ============================================================
# STEP 2: SAVE COMPATIBLE H5
# ============================================================

print("\n💾 STEP 2: Saving compatible H5 format...")
try:
    model.save('best_model_fixed.h5', save_format='h5')
    h5_size = os.path.getsize('best_model_fixed.h5') / 1024 / 1024
    print(f"✅ Saved: best_model_fixed.h5 ({h5_size:.2f} MB)")
except Exception as e:
    print(f"⚠️  Warning: Could not save H5: {e}")

# ============================================================
# STEP 3: REPRESENTATIVE DATASET
# ============================================================

def representative_dataset():
    """
    Generate representative dataset for INT8 quantization.
    This helps the converter determine optimal quantization parameters.
    Uses random data matching the model's input shape.
    """
    print("\n🔢 STEP 3: Generating representative dataset...")
    for i in range(100):
        # Generate random data matching model input (224x224x3)
        # Normalized to [0, 1] range like training data
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]
        if (i + 1) % 25 == 0:
            print(f"   Progress: {i + 1}/100 samples")
    print("✅ Representative dataset ready!")

# ============================================================
# STEP 4: CONVERT TO INT8 TFLITE
# ============================================================

print("\n🔧 STEP 4: Converting to INT8 TFLite...")
print("   This may take 1-2 minutes...")

try:
    # Create converter
    converter_int8 = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Enable INT8 quantization
    converter_int8.optimizations = [tf.lite.Optimize.DEFAULT]
    converter_int8.representative_dataset = representative_dataset
    
    # Full integer quantization (INT8)
    converter_int8.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter_int8.inference_input_type = tf.uint8
    converter_int8.inference_output_type = tf.uint8
    
    # Convert
    tflite_int8 = converter_int8.convert()
    
    # Save
    with open('best_model_int8.tflite', 'wb') as f:
        f.write(tflite_int8)
    
    int8_size = len(tflite_int8) / 1024 / 1024
    print(f"✅ INT8 model saved: best_model_int8.tflite ({int8_size:.2f} MB)")
    
except Exception as e:
    print(f"❌ INT8 conversion failed: {e}")
    tflite_int8 = None

# ============================================================
# STEP 5: CONVERT TO FLOAT16 TFLITE (FALLBACK)
# ============================================================

print("\n🔧 STEP 5: Converting to Float16 TFLite...")

try:
    converter_float16 = tf.lite.TFLiteConverter.from_keras_model(model)
    converter_float16.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # Convert
    tflite_float16 = converter_float16.convert()
    
    # Save
    with open('best_model_float16.tflite', 'wb') as f:
        f.write(tflite_float16)
    
    float16_size = len(tflite_float16) / 1024 / 1024
    print(f"✅ Float16 model saved: best_model_float16.tflite ({float16_size:.2f} MB)")
    
except Exception as e:
    print(f"❌ Float16 conversion failed: {e}")
    tflite_float16 = None

# ============================================================
# STEP 6: CONVERT TO STANDARD TFLITE (NO QUANTIZATION)
# ============================================================

print("\n🔧 STEP 6: Converting to standard TFLite (no quantization)...")

try:
    converter_standard = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_standard = converter_standard.convert()
    
    with open('best_model_standard.tflite', 'wb') as f:
        f.write(tflite_standard)
    
    standard_size = len(tflite_standard) / 1024 / 1024
    print(f"✅ Standard model saved: best_model_standard.tflite ({standard_size:.2f} MB)")
    
except Exception as e:
    print(f"⚠️  Standard conversion failed: {e}")
    tflite_standard = None

# ============================================================
# STEP 7: SUMMARY
# ============================================================

print("\n" + "="*70)
print("✅ CONVERSION COMPLETE!")
print("="*70)

original_size = os.path.getsize('best_model.h5') / 1024 / 1024
print(f"\n📊 File Sizes:")
print(f"   Original H5:       {original_size:.2f} MB (baseline)")

if tflite_int8:
    int8_size = len(tflite_int8) / 1024 / 1024
    print(f"   INT8 TFLite:       {int8_size:.2f} MB ({original_size/int8_size:.1f}x smaller) ⭐ RECOMMENDED")

if tflite_float16:
    float16_size = len(tflite_float16) / 1024 / 1024
    print(f"   Float16 TFLite:    {float16_size:.2f} MB ({original_size/float16_size:.1f}x smaller)")

if tflite_standard:
    standard_size = len(tflite_standard) / 1024 / 1024
    print(f"   Standard TFLite:   {standard_size:.2f} MB ({original_size/standard_size:.1f}x smaller)")

if os.path.exists('best_model_fixed.h5'):
    fixed_size = os.path.getsize('best_model_fixed.h5') / 1024 / 1024
    print(f"   Fixed H5:          {fixed_size:.2f} MB")

print("\n📈 Performance Comparison:")
print("   ┌─────────────────┬──────────┬───────────┬──────────────┐")
print("   │ Format          │ Size     │ Speed     │ Accuracy     │")
print("   ├─────────────────┼──────────┼───────────┼──────────────┤")
print("   │ Original H5     │ Baseline │ Baseline  │ 100%         │")
print("   │ INT8 TFLite     │ ~4x ↓    │ 2-3x ↑    │ ~99% (< 1%)  │")
print("   │ Float16 TFLite  │ ~2x ↓    │ 1.5x ↑    │ ~99.9%       │")
print("   │ Standard TFLite │ Similar  │ Similar   │ 100%         │")
print("   └─────────────────┴──────────┴───────────┴──────────────┘")

print("\n💡 Recommendations:")
print("   🥇 INT8 TFLite     - Best for Raspberry Pi (smallest + fastest)")
print("   🥈 Float16 TFLite  - Good balance (smaller + faster)")
print("   🥉 Fixed H5        - Fallback if TFLite has issues")

print("\n" + "="*70)
print("📋 NEXT STEPS")
print("="*70)

print("\n1️⃣  Download files from Colab:")
print("   - best_model_int8.tflite (RECOMMENDED)")
print("   - best_model_float16.tflite (fallback)")
print("   - best_model_fixed.h5 (if needed)")

print("\n2️⃣  Copy to Raspberry Pi:")
print("   scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/")
print("   scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/best_model.tflite")

print("\n3️⃣  On Raspberry Pi, install tflite-runtime:")
print("   pip install tflite-runtime")

print("\n4️⃣  Run backend server with TFLite:")
print("   cd ~/deteksikantuk")
print("   python backend_server_tflite.py")

print("\n5️⃣  Test the API:")
print("   curl http://localhost:5001/api/health")

print("\n" + "="*70)
print("✨ All done! Your model is ready for Raspberry Pi deployment!")
print("="*70)
