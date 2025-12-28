"""
Convert H5 to TFLite di Raspberry Pi
====================================
Jalankan di Raspberry Pi setelah transfer model_exp3.h5
"""

import tensorflow as tf
from tensorflow import keras
import os
import hashlib

print("="*60)
print("🔄 Converting H5 to Compatible TFLite")
print("="*60)
print(f"TensorFlow: {tf.__version__}")
print(f"Keras: {keras.__version__}")
try:
    import numpy as np
    print(f"NumPy: {np.__version__}")
except:
    pass
print()

# Path model H5
MODEL_H5 = "model_exp3.h5"

if not os.path.exists(MODEL_H5):
    print(f"❌ File not found: {MODEL_H5}")
    print("   Transfer file dari Colab dulu!")
    exit(1)

# Load model
print(f"1. Loading {MODEL_H5}...")
model = None

# Try standard Keras first (Keras 3 in TF 2.19+)
try:
    model = keras.models.load_model(MODEL_H5, compile=False)
    print(f"   ✅ Loaded with Keras {keras.__version__}!")
    print(f"   Input: {model.input_shape}")
    print(f"   Output: {model.output_shape}")
except Exception as e:
    print(f"   ⚠️  Standard loading failed: {e}")
    
    # Try with legacy Keras mode (for models trained with Keras 2)
    print("\n   Trying with legacy Keras mode (TF_USE_LEGACY_KERAS=1)...")
    try:
        os.environ["TF_USE_LEGACY_KERAS"] = "1"
        # Need to reimport after setting env var
        import importlib
        importlib.reload(tf)
        from tensorflow import keras as keras_legacy
        model = keras_legacy.models.load_model(MODEL_H5, compile=False)
        print(f"   ✅ Loaded with legacy Keras mode!")
        print(f"   Input: {model.input_shape}")
        print(f"   Output: {model.output_shape}")
    except Exception as e2:
        print(f"   ❌ Legacy mode failed: {e2}")
        
        # Last resort: try tf_keras
        print("\n   Trying with tf_keras package...")
        try:
            import tf_keras
            model = tf_keras.models.load_model(MODEL_H5, compile=False)
            print(f"   ✅ Loaded with tf_keras!")
            print(f"   Input: {model.input_shape}")
            print(f"   Output: {model.output_shape}")
        except Exception as e3:
            print(f"   ❌ All loading methods failed!")
            print(f"\n   Error details:")
            print(f"   - Standard Keras: {e}")
            print(f"   - Legacy mode: {e2}")
            print(f"   - tf_keras: {e3}")
            exit(1)

if model is None:
    print("   ❌ Failed to load model!")
    exit(1)

# Convert to TFLite
print(f"\n2. Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# CRITICAL: Compatibility settings for Raspberry Pi
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS
]
converter.optimizations = [tf.lite.Optimize.DEFAULT]

try:
    tflite_model = converter.convert()
    print("   ✅ Converted!")
except Exception as e:
    print(f"   ❌ Conversion failed: {e}")
    exit(1)

# Save
OUTPUT = "best_model_raspi.tflite"
with open(OUTPUT, 'wb') as f:
    f.write(tflite_model)

size_mb = len(tflite_model) / (1024 * 1024)
print(f"   Size: {size_mb:.2f} MB")

# Test loading
print(f"\n3. Testing {OUTPUT}...")
try:
    interpreter = tf.lite.Interpreter(model_path=OUTPUT)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print("   ✅ Loads successfully!")
    print(f"   Input: {input_details[0]['shape']}")
    print(f"   Output: {output_details[0]['shape']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Model may not be compatible!")
    exit(1)

# MD5 verification
with open(OUTPUT, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()

print(f"\n4. Verification:")
print(f"   MD5 New: {md5}")
print(f"   MD5 Old: 7fda967f167768f53531c3477687ed50")

if md5 == "7fda967f167768f53531c3477687ed50":
    print("\n   ❌ WARNING: Same MD5 - conversion may have failed!")
    print("   But if it loads OK, it might still work.")
else:
    print("\n   ✅ Different MD5 - conversion successful!")

print("\n" + "="*60)
print("✅ DONE!")
print("="*60)
print(f"\nFile created: {OUTPUT}")
print("\nNext steps:")
print(f"1. cp {OUTPUT} best_model_compatible.tflite")
print("2. python3 app.py")
print("="*60)
