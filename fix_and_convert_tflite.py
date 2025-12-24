"""
Fix Model and Convert to TFLite INT8
=====================================
This script fixes the batch_shape error and converts to TFLite with INT8 quantization
"""

import tensorflow as tf
import numpy as np
import os

print("="*60)
print("🔄 FIX MODEL & CONVERT TO TFLITE INT8")
print("="*60)

# Step 1: Load model with custom object scope to handle batch_shape
print("\n📦 Step 1: Loading H5 model with compatibility fix...")

try:
    # Try loading normally first
    model = tf.keras.models.load_model('best_model.h5', compile=False)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"⚠️  Normal loading failed: {e}")
    print("🔧 Trying alternative loading method...")
    
    # Alternative: Load weights only
    try:
        # Recreate model architecture (MobileNetV2 based)
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
        from tensorflow.keras.models import Model
        
        print("   Building model architecture...")
        base_model = MobileNetV2(input_shape=(224, 224, 3), 
                                include_top=False, 
                                weights=None)
        
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.5)(x)
        predictions = Dense(4, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        
        # Load weights
        print("   Loading weights from H5 file...")
        model.load_weights('best_model.h5')
        print("✅ Model reconstructed and weights loaded!")
        
    except Exception as e2:
        print(f"❌ Failed to load model: {e2}")
        print("\n💡 SOLUTION: Run this script on your LAPTOP first!")
        print("   Then copy the generated .tflite file to Raspberry Pi")
        exit(1)

# Print model info
print(f"\n📊 Model Information:")
print(f"   Input shape:  {model.input_shape}")
print(f"   Output shape: {model.output_shape}")
print(f"   Total params: {model.count_params():,}")

# Step 2: Save in compatible format
print("\n💾 Step 2: Saving in compatible format...")
model.save('best_model_fixed.h5', save_format='h5')
print("✅ Saved as best_model_fixed.h5")

# Step 3: Representative dataset for INT8 quantization
def representative_dataset():
    """
    Generate representative dataset for INT8 quantization
    This helps determine optimal quantization parameters
    """
    print("\n🔢 Step 3: Generating representative dataset for INT8 quantization...")
    for i in range(100):
        # Generate random data matching model input (224x224x3)
        # Normalize to [0, 1] range like training data
        data = np.random.rand(1, 224, 224, 3).astype(np.float32)
        yield [data]
        if (i + 1) % 25 == 0:
            print(f"   Generated {i + 1}/100 samples...")

# Step 4: Convert to TFLite with INT8 quantization
print("\n🔧 Step 4: Creating TFLite converter with INT8 quantization...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable INT8 quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset

# Full integer quantization
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

print("\n⚙️  Converting to TFLite INT8...")
tflite_model_int8 = converter.convert()

# Save INT8 model
output_int8 = 'best_model_int8.tflite'
with open(output_int8, 'wb') as f:
    f.write(tflite_model_int8)
print(f"✅ INT8 model saved as {output_int8}")

# Step 5: Also create standard TFLite (float16) for comparison
print("\n🔧 Step 5: Creating standard TFLite (float16) for comparison...")
converter2 = tf.lite.TFLiteConverter.from_keras_model(model)
converter2.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model_float16 = converter2.convert()

output_float16 = 'best_model_float16.tflite'
with open(output_float16, 'wb') as f:
    f.write(tflite_model_float16)
print(f"✅ Float16 model saved as {output_float16}")

# Print results
h5_size = os.path.getsize('best_model.h5') / 1024 / 1024
int8_size = len(tflite_model_int8) / 1024 / 1024
float16_size = len(tflite_model_float16) / 1024 / 1024

print("\n" + "="*60)
print("✅ CONVERSION COMPLETE!")
print("="*60)
print(f"Original H5:        {h5_size:.2f} MB")
print(f"TFLite INT8:        {int8_size:.2f} MB ({h5_size/int8_size:.1f}x smaller)")
print(f"TFLite Float16:     {float16_size:.2f} MB ({h5_size/float16_size:.1f}x smaller)")
print(f"\nINT8 vs Float16:    {float16_size/int8_size:.1f}x smaller")
print(f"TensorFlow version: {tf.__version__}")
print("="*60)

print("\n📋 NEXT STEPS:")
print("\n1️⃣  Copy to Raspberry Pi:")
print(f"   scp {output_int8} entung@192.168.0.108:~/deteksikantuk/")
print(f"   scp best_model_fixed.h5 entung@192.168.0.108:~/deteksikantuk/")

print("\n2️⃣  On Raspberry Pi, backup old model:")
print("   cd ~/deteksikantuk")
print("   mv best_model.h5 best_model_old.h5")
print("   mv best_model_fixed.h5 best_model.h5")

print("\n3️⃣  Test with TFLite backend:")
print("   python backend_server_tflite.py")

print("\n💡 TIPS:")
print("   - INT8 model is ~4x smaller and 2-3x faster")
print("   - Accuracy loss is typically < 1%")
print("   - Perfect for Raspberry Pi!")
print("   - Use backend_server_tflite.py for TFLite inference")
