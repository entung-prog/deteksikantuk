"""
Fix Model and Save in Multiple Formats
========================================
Run this script to convert best_model.h5 to compatible formats
"""

import tensorflow as tf
import os

print("="*60)
print("🔧 FIX MODEL - MULTIPLE FORMAT CONVERTER")
print("="*60)

# Try to load the model
print("\n📦 Loading best_model.h5...")

model = None
method = None

# Method 1: Direct load with compile=False
try:
    print("   Method 1: Direct load...")
    model = tf.keras.models.load_model('best_model.h5', compile=False)
    method = "Direct load"
    print("✅ Success!")
except Exception as e1:
    print(f"   ❌ Failed: {str(e1)[:80]}")
    
    # Method 2: Load with custom objects
    try:
        print("   Method 2: Custom objects...")
        model = tf.keras.models.load_model('best_model.h5', compile=False, 
                                          custom_objects={'batch_shape': None})
        method = "Custom objects"
        print("✅ Success!")
    except Exception as e2:
        print(f"   ❌ Failed: {str(e2)[:80]}")
        print("\n❌ Cannot load model!")
        print("   Please run this script on the machine where model was trained.")
        exit(1)

if model is None:
    print("❌ Failed to load model")
    exit(1)

print(f"\n✅ Model loaded using: {method}")
print(f"   Input shape:  {model.input_shape}")
print(f"   Output shape: {model.output_shape}")

# Save in multiple formats
print("\n💾 Saving in multiple formats...")

# 1. SavedModel format (most compatible)
print("\n1️⃣  SavedModel format...")
try:
    tf.saved_model.save(model, 'saved_model')
    print("✅ Saved: saved_model/")
except Exception as e:
    print(f"❌ Failed: {e}")

# 2. H5 format (re-save with current TF version)
print("\n2️⃣  H5 format...")
try:
    model.save('best_model_fixed.h5', save_format='h5')
    h5_size = os.path.getsize('best_model_fixed.h5') / 1024 / 1024
    print(f"✅ Saved: best_model_fixed.h5 ({h5_size:.2f} MB)")
except Exception as e:
    print(f"❌ Failed: {e}")

# 3. Weights only
print("\n3️⃣  Weights only...")
try:
    model.save_weights('model_weights_fixed.h5')
    weights_size = os.path.getsize('model_weights_fixed.h5') / 1024 / 1024
    print(f"✅ Saved: model_weights_fixed.h5 ({weights_size:.2f} MB)")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n" + "="*60)
print("✅ CONVERSION COMPLETE!")
print("="*60)

print("\n📋 Files created:")
if os.path.exists('saved_model'):
    print("   ✅ saved_model/ (TensorFlow SavedModel)")
if os.path.exists('best_model_fixed.h5'):
    print("   ✅ best_model_fixed.h5 (Fixed H5)")
if os.path.exists('model_weights_fixed.h5'):
    print("   ✅ model_weights_fixed.h5 (Weights only)")

print("\n💡 Next steps:")
print("   Use backend_server.py with best_model_fixed.h5")
print("   Or use backend_server_savedmodel.py with saved_model/")
