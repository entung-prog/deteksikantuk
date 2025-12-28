"""
RETRAIN Model dengan TensorFlow 2.15 di Colab
==============================================
Ini adalah SATU-SATUNYA cara untuk mendapatkan model yang kompatibel.

PENTING: Jalankan di Colab BARU (fresh runtime)
"""

# Step 1: Install TensorFlow 2.15
print("Installing TensorFlow 2.15...")
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", 
                      "tensorflow==2.15.0", 
                      "tf-keras==2.15.0"])

print("\n⚠️  RESTART RUNTIME sekarang!")
print("   Klik: Runtime → Restart runtime")
print("   Lalu jalankan cell berikutnya!")
