"""
Download H5 Model dari Colab
=============================
Script sederhana untuk download model H5
"""

from google.colab import drive, files
drive.mount('/content/drive')

# Path ke model H5
MODEL_H5 = '/content/drive/MyDrive/parameter_testing_results/model_exp3.h5'

print("="*60)
print("📥 Downloading Model H5")
print("="*60)
print(f"\nFile: {MODEL_H5}")

# Download langsung
files.download(MODEL_H5)

print("\n✅ DONE!")
print("\nNext: Transfer model_exp3.h5 ke Raspberry Pi:")
print("scp model_exp3.h5 entung@192.168.18.150:/home/entung/deteksikantuk/backend/")
