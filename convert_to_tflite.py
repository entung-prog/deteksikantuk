"""
Convert H5 Model to TensorFlow Lite with INT8 Quantization
===========================================================
This script converts the drowsiness detection model to TFLite format
for better performance on Raspberry Pi.
"""

import tensorflow as tf
import numpy as np
import os

print("="*60)
print("🔄 CONVERTING MODEL TO TENSORFLOW LITE")
print("="*60)

# Load H5 model
print("\n📦 Loading H5 model...")
model = tf.keras.models.load_model('best_model.h5')
print("✅ Model loaded successfully!")

# Print model info
print(f"\nModel input shape: {model.input_shape}")
print(f"Model output shape: {model.output_shape}")

# Representative dataset for quantization
def representative_dataset():
    """
    Generate representative dataset for INT8 quantization
    This helps the converter determine optimal quantization parameters
    """
    print("\n🔢 Generating representative dataset for quantization...")
    for i in range(100):
        # Generate random data with same shape as model input (224x224x3)
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]
        if (i + 1) % 20 == 0:
            print(f"  Generated {i + 1}/100 samples...")

# Create converter
print("\n🔧 Creating TFLite converter...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable basic optimizations (float16 quantization)
print("⚙️  Enabling optimizations...")
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
print("\n🔄 Converting model...")
tflite_model = converter.convert()


# Save TFLite model
output_file = 'best_model.tflite'
print(f"\n💾 Saving TFLite model to {output_file}...")
with open(output_file, 'wb') as f:
    f.write(tflite_model)

# Print results
h5_size = os.path.getsize('best_model.h5') / 1024 / 1024
tflite_size = len(tflite_model) / 1024 / 1024
compression_ratio = h5_size / tflite_size

print("\n" + "="*60)
print("✅ CONVERSION COMPLETE!")
print("="*60)
print(f"Original H5 size:  {h5_size:.2f} MB")
print(f"TFLite size:       {tflite_size:.2f} MB")
print(f"Compression ratio: {compression_ratio:.1f}x smaller")
print(f"Size reduction:    {(1 - tflite_size/h5_size) * 100:.1f}%")
print("="*60)

print("\n📋 Next steps:")
print("1. Copy best_model.tflite to Raspberry Pi:")
print("   scp best_model.tflite entung@192.168.0.108:~/deteksikantuk/")
print("\n2. Use backend_server_tflite.py on Raspberry Pi")
print("\n3. Install tflite-runtime on Raspberry Pi:")
print("   pip install tflite-runtime")
