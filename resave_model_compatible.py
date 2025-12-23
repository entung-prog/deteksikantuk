"""
Re-save Model in Compatible Format
===================================
Fix for "Unrecognized keyword arguments: batch_shape" error
"""

import tensorflow as tf
import os

print("="*60)
print("🔄 RE-SAVING MODEL IN COMPATIBLE FORMAT")
print("="*60)

# Check if model exists
if not os.path.exists('best_model.h5'):
    print("❌ ERROR: best_model.h5 not found!")
    print("   Make sure you're in the webtest folder")
    exit(1)

print("\n📦 Loading original model...")
try:
    model = tf.keras.models.load_model('best_model.h5')
    print("✅ Model loaded successfully")
    print(f"   Input shape: {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)

print("\n💾 Saving in compatible format...")

# Save as H5 with current TensorFlow version
output_file = 'best_model_v2.h5'
model.save(output_file, save_format='h5')
print(f"✅ Saved as {output_file}")

# Get file sizes
original_size = os.path.getsize('best_model.h5') / 1024 / 1024
new_size = os.path.getsize(output_file) / 1024 / 1024

print("\n" + "="*60)
print("✅ CONVERSION COMPLETE!")
print("="*60)
print(f"Original file:  best_model.h5 ({original_size:.2f} MB)")
print(f"New file:       {output_file} ({new_size:.2f} MB)")
print(f"TensorFlow:     {tf.__version__}")
print("="*60)

print("\n📋 Next steps:")
print("1. Copy to Raspberry Pi:")
print(f"   scp {output_file} entung@192.168.0.100:~/deteksikantuk/")
print("\n2. On Raspberry Pi:")
print("   cd ~/deteksikantuk")
print("   mv best_model.h5 best_model_old.h5")
print(f"   mv {output_file} best_model.h5")
print("\n3. Run backend:")
print("   python backend_server.py")
