"""
Test Script - Jalankan di Colab SETELAH konversi
Untuk memastikan model sudah kompatibel
"""

import tensorflow as tf
import os

print("="*60)
print("🧪 Testing Converted Model")
print("="*60)

MODEL_PATH = "best_model_compatible.tflite"

if not os.path.exists(MODEL_PATH):
    print(f"❌ File not found: {MODEL_PATH}")
    print("   Pastikan konversi sudah dijalankan!")
else:
    print(f"✅ File found: {MODEL_PATH}")
    print(f"   Size: {os.path.getsize(MODEL_PATH) / (1024*1024):.2f} MB")
    
    # Check MD5 (untuk compare dengan file lama)
    import hashlib
    with open(MODEL_PATH, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    print(f"   MD5: {md5}")
    
    # Try loading
    print("\n🔍 Testing TFLite interpreter...")
    try:
        interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()
        print("✅ Model loads successfully!")
        
        # Check operations
        print("\n📋 Checking operations...")
        details = interpreter.get_tensor_details()
        print(f"   Total tensors: {len(details)}")
        
        # This should work if conversion was successful
        print("\n✅ Model is compatible!")
        print("\n⚠️  IMPORTANT: MD5 hash harus BERBEDA dari file lama!")
        print("   File lama MD5: 7fda967f167768f53531c3477687ed50")
        print(f"   File baru MD5: {md5}")
        
        if md5 == "7fda967f167768f53531c3477687ed50":
            print("\n❌ WARNING: File ini SAMA dengan file lama!")
            print("   Konversi mungkin gagal atau file salah!")
        else:
            print("\n✅ File berbeda - konversi berhasil!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n   Ini berarti konversi GAGAL!")
        print("   Coba jalankan ulang script konversi")

print("\n" + "="*60)
