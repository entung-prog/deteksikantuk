"""
Convert Model (Jalankan SETELAH restart runtime)
=================================================
"""

# Mount Drive
from google.colab import drive, files
drive.mount('/content/drive')

import tensorflow as tf
from tensorflow import keras
import os
import hashlib

print("="*60)
print(f"TensorFlow version: {tf.__version__}")
print("="*60)

# HARUS 2.15.x
if not tf.__version__.startswith('2.15'):
    print(f"\n❌ ERROR: TensorFlow version {tf.__version__}")
    print("   Harus 2.15.x!")
    print("   Jalankan cell sebelumnya dan restart runtime!")
else:
    print("✅ TensorFlow 2.15 - OK!\n")
    
    # Load model
    MODEL_PATH = '/content/drive/MyDrive/parameter_testing_results/model_exp3.h5'
    print(f"Loading: {MODEL_PATH}")
    model = keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Model loaded!\n")
    
    # Convert
    print("Converting...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    tflite_model = converter.convert()
    print("✅ Converted!\n")
    
    # Save
    OUTPUT = "model_tf215_compatible.tflite"
    with open(OUTPUT, 'wb') as f:
        f.write(tflite_model)
    
    # Test
    print("Testing...")
    interp = tf.lite.Interpreter(model_path=OUTPUT)
    interp.allocate_tensors()
    print("✅ Loads OK!\n")
    
    # MD5
    with open(OUTPUT, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    
    print(f"Size: {len(tflite_model)/(1024*1024):.2f} MB")
    print(f"MD5:  {md5}")
    print(f"Old:  7fda967f167768f53531c3477687ed50")
    
    if md5 == "7fda967f167768f53531c3477687ed50":
        print("\n❌ SAMA - Konversi gagal!")
    else:
        print("\n✅ BEDA - Konversi berhasil!")
        
        # Download
        print("\nDownloading...")
        files.download(OUTPUT)
        print("\n✅ DONE!")
        print(f"\nTransfer: scp {OUTPUT} entung@192.168.18.150:/home/entung/deteksikantuk/backend/best_model_compatible.tflite")
