# 🚀 Simple Deployment Steps

## Masalah: Permission Denied

Script otomatis gagal karena masalah permission. Mari gunakan cara manual yang lebih mudah.

---

## ✅ Solusi: Copy Files Manual

### **Step 1: Copy Files ke Raspberry Pi**

**Jalankan script batch ini di PowerShell:**

```cmd
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
.\copy_files.bat
```

Script akan copy semua file satu per satu. **Masukkan password** setiap kali diminta.

**Atau copy manual satu per satu:**

```powershell
# Buat directory
ssh entung@192.168.0.108 "mkdir -p ~/drowsiness-detection"

# Copy files
scp backend_server.py entung@192.168.0.108:~/drowsiness-detection/
scp drowsiness_test.html entung@192.168.0.108:~/drowsiness-detection/
scp drowsiness_test.css entung@192.168.0.108:~/drowsiness-detection/
scp drowsiness_test_hybrid.js entung@192.168.0.108:~/drowsiness-detection/
scp requirements.txt entung@192.168.0.108:~/drowsiness-detection/
scp deploy.sh entung@192.168.0.108:~/drowsiness-detection/
scp ..\best_model.h5 entung@192.168.0.108:~/drowsiness-detection/
```

---

### **Step 2: SSH ke Raspberry Pi**

```powershell
ssh entung@192.168.0.108
```

---

### **Step 3: Jalankan Deployment**

**Di Raspberry Pi (terminal SSH):**

```bash
cd ~/drowsiness-detection

# Verify files ada
ls -la

# Jalankan deployment
chmod +x deploy.sh
./deploy.sh
```

Script akan otomatis:
- Install dependencies
- Setup Python virtual environment
- Install packages
- Setup systemd services
- Start aplikasi

---

### **Step 4: Verify**

```bash
# Cek service status
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-web

# Cek IP address
hostname -I
```

---

### **Step 5: Akses dari Browser**

```
http://192.168.0.108:8000/drowsiness_test.html
```

---

## 🔑 Tip: Setup SSH Key (Agar Tidak Perlu Password)

**Di Windows PowerShell:**

```powershell
# Generate SSH key (jika belum ada)
ssh-keygen -t rsa -b 4096
# Tekan Enter untuk semua pertanyaan (default)

# Copy public key ke Raspberry Pi
Get-Content $env:USERPROFILE\.ssh\id_rsa.pub | ssh entung@192.168.0.108 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Setelah itu, SSH dan SCP tidak perlu password lagi!

---

**Mulai dari Step 1!** 🚀
