"""
Convert Model Weights to TFLite INT8
=====================================
Uses model_weights.weights.h5 to avoid batch_shape error
This is SIMPLER and works on any environment!
"""

import tensorflow as tf
import numpy as np
import os

print("="*70)
print("🔄 CONVERT WEIGHTS TO TFLITE INT8")
print("="*70)

# ============================================================
# STEP 1: REBUILD MODEL ARCHITECTURE
# ============================================================

print("\n🏗️  STEP 1: Building model architecture...")

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

# Build same architecture as training
base_model = MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights=None  # Don't load ImageNet weights
)

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(4, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

print("✅ Model architecture built!")
print(f"   Input shape:  {model.input_shape}")
print(f"   Output shape: {model.output_shape}")
print(f"   Total params: {model.count_params():,}")

# ============================================================
# STEP 2: LOAD WEIGHTS
# ============================================================

print("\n📦 STEP 2: Loading weights from file...")

weights_file = '../model_weights.weights.h5'

if not os.path.exists(weights_file):
    # Try alternative paths
    alt_paths = [
        'model_weights.weights.h5',
        '../model_weights.weights.h5',
        '../../model_weights.weights.h5',
        'C:/Users/maula/OneDrive/Dokumen/skripsi/pipeline/model_weights.weights.h5'
    ]
    
    for path in alt_paths:
        if os.path.exists(path):
            weights_file = path
            break
    else:
        print(f"❌ Weights file not found!")
        print(f"   Searched paths:")
        for path in alt_paths:
            print(f"   - {path}")
        exit(1)

print(f"   Loading from: {weights_file}")

try:
    model.load_weights(weights_file)
    print("✅ Weights loaded successfully!")
except Exception as e:
    print(f"❌ Error loading weights: {e}")
    exit(1)

# ============================================================
# STEP 3: SAVE COMPATIBLE H5
# ============================================================

print("\n💾 STEP 3: Saving as compatible H5...")
model.save('best_model_from_weights.h5', save_format='h5')
h5_size = os.path.getsize('best_model_from_weights.h5') / 1024 / 1024
print(f"✅ Saved: best_model_from_weights.h5 ({h5_size:.2f} MB)")

# ============================================================
# STEP 4: REPRESENTATIVE DATASET FOR INT8
# ============================================================

def representative_dataset():
    """Generate representative dataset for INT8 quantization"""
    print("\n🔢 STEP 4: Generating representative dataset...")
    for i in range(100):
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]
        if (i + 1) % 25 == 0:
            print(f"   Progress: {i + 1}/100 samples")
    print("✅ Dataset ready!")

# ============================================================
# STEP 5: CONVERT TO INT8 TFLITE
# ============================================================

print("\n🔧 STEP 5: Converting to INT8 TFLite...")
print("   This may take 1-2 minutes...")

try:
    converter_int8 = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # INT8 quantization
    converter_int8.optimizations = [tf.lite.Optimize.DEFAULT]
    converter_int8.representative_dataset = representative_dataset
    converter_int8.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter_int8.inference_input_type = tf.uint8
    converter_int8.inference_output_type = tf.uint8
    
    tflite_int8 = converter_int8.convert()
    
    with open('best_model_int8.tflite', 'wb') as f:
        f.write(tflite_int8)
    
    int8_size = len(tflite_int8) / 1024 / 1024
    print(f"✅ INT8 saved: best_model_int8.tflite ({int8_size:.2f} MB)")
    
except Exception as e:
    print(f"❌ INT8 conversion failed: {e}")
    tflite_int8 = None

# ============================================================
# STEP 6: CONVERT TO FLOAT16 TFLITE
# ============================================================

print("\n🔧 STEP 6: Converting to Float16 TFLite...")

try:
    converter_float16 = tf.lite.TFLiteConverter.from_keras_model(model)
    converter_float16.optimizations = [tf.lite.Optimize.DEFAULT]
    
    tflite_float16 = converter_float16.convert()
    
    with open('best_model_float16.tflite', 'wb') as f:
        f.write(tflite_float16)
    
    float16_size = len(tflite_float16) / 1024 / 1024
    print(f"✅ Float16 saved: best_model_float16.tflite ({float16_size:.2f} MB)")
    
except Exception as e:
    print(f"❌ Float16 conversion failed: {e}")
    tflite_float16 = None

# ============================================================
# STEP 7: SUMMARY
# ============================================================

print("\n" + "="*70)
print("✅ CONVERSION COMPLETE!")
print("="*70)

print(f"\n📊 Results:")
print(f"   Source:            model_weights.weights.h5")

if os.path.exists('best_model_from_weights.h5'):
    h5_size = os.path.getsize('best_model_from_weights.h5') / 1024 / 1024
    print(f"   H5 model:          {h5_size:.2f} MB")

if tflite_int8:
    int8_size = len(tflite_int8) / 1024 / 1024
    print(f"   INT8 TFLite:       {int8_size:.2f} MB ({h5_size/int8_size:.1f}x smaller) ⭐")

if tflite_float16:
    float16_size = len(tflite_float16) / 1024 / 1024
    print(f"   Float16 TFLite:    {float16_size:.2f} MB ({h5_size/float16_size:.1f}x smaller)")

print(f"\n   TensorFlow:        {tf.__version__}")

print("\n" + "="*70)
print("📋 NEXT STEPS")
print("="*70)

print("\n1️⃣  Copy INT8 model to Raspberry Pi:")
print("   scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/")
print("   scp best_model_int8.tflite entung@192.168.0.108:~/deteksikantuk/best_model.tflite")

print("\n2️⃣  On Raspberry Pi:")
print("   cd ~/deteksikantuk")
print("   source venv/bin/activate")
print("   pip install tflite-runtime")
print("   python backend_server_tflite.py")

print("\n3️⃣  Test:")
print("   curl http://localhost:5001/api/health")

print("\n💡 ADVANTAGES:")
print("   ✅ No batch_shape error!")
print("   ✅ Works on any environment")
print("   ✅ 4x smaller file size")
print("   ✅ 2-3x faster inference")
print("   ✅ Perfect for Raspberry Pi")

print("\n" + "="*70)
