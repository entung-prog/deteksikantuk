"""
Alternative Solution: Convert via SavedModel
=============================================
Karena TF 2.15 tidak bisa install di Colab (Python 3.12),
kita akan export ke SavedModel dulu, lalu convert di Raspberry Pi
"""

from google.colab import drive, files
drive.mount('/content/drive')

import tensorflow as tf
from tensorflow import keras
import os

print("="*60)
print(f"TensorFlow: {tf.__version__}")
print("="*60)

# Load model H5
MODEL_H5 = '/content/drive/MyDrive/parameter_testing_results/model_exp3.h5'
print(f"\n1. Loading H5: {MODEL_H5}")
model = keras.models.load_model(MODEL_H5, compile=False)
print("   ✅ Loaded!")

# Export ke SavedModel format (lebih portable)
SAVED_MODEL_DIR = "saved_model_export"
print(f"\n2. Exporting to SavedModel format...")
model.save(SAVED_MODEL_DIR, save_format='tf')
print(f"   ✅ Exported to: {SAVED_MODEL_DIR}")

# Zip untuk download
print("\n3. Creating zip file...")
import shutil
shutil.make_archive("saved_model_export", 'zip', SAVED_MODEL_DIR)
print("   ✅ Zipped!")

# Download
print("\n4. Downloading...")
files.download("saved_model_export.zip")

print("\n" + "="*60)
print("✅ DONE!")
print("="*60)
print("\nNext steps:")
print("1. Transfer saved_model_export.zip ke Raspberry Pi")
print("2. Saya akan convert di Raspberry Pi dengan TF 2.15")
print("="*60)
