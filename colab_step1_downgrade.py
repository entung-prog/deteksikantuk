"""
Convert dengan TensorFlow 2.15 di Colab
=======================================
Script ini akan downgrade TensorFlow ke 2.15 untuk konversi
"""

print("="*60)
print("🔄 Downgrading TensorFlow to 2.15")
print("="*60)

# Uninstall TF 2.19 dan install TF 2.15
import subprocess
import sys

print("\n1. Uninstalling TensorFlow 2.19...")
subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "tensorflow"])

print("\n2. Installing TensorFlow 2.15...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "tensorflow==2.15.0"])

print("\n3. Restarting runtime...")
print("   ⚠️  PENTING: Setelah install, klik 'Runtime' -> 'Restart runtime'")
print("   Lalu jalankan cell berikutnya!\n")
print("="*60)
