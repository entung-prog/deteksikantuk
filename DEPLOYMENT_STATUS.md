# 🚀 Deployment - Ready to Deploy!

## ✅ SSH Connection Berhasil!

**Informasi Raspberry Pi Anda:**
- IP Address: `192.168.0.108`
- Username: `entung`
- SSH: ✅ Working

---

## 📦 Deployment Sedang Berjalan

Script deployment sudah dimulai dan sedang menunggu password Anda.

**Di terminal PowerShell, masukkan password untuk user `entung`**

Script akan otomatis:
1. ✅ Membuat directory `/home/entung/drowsiness-detection`
2. ✅ Copy semua file aplikasi
3. ✅ Copy model file `best_model.h5`
4. ✅ Memberikan instruksi selanjutnya

---

## 🔑 Setelah File Transfer Selesai

Jalankan command ini untuk deployment di Raspberry Pi:

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Masuk ke directory aplikasi
cd /home/entung/drowsiness-detection

# Jalankan deployment script
chmod +x deploy.sh
./deploy.sh
```

---

## 💡 Tip: Setup SSH Key (Opsional)

Agar tidak perlu password setiap kali, setup SSH key:

**Di Windows:**
```powershell
# Generate SSH key (jika belum punya)
ssh-keygen -t rsa -b 4096

# Copy public key ke Raspberry Pi
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh entung@192.168.0.108 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Setelah itu, SSH dan SCP tidak perlu password lagi!

---

## 📝 Quick Commands

```powershell
# Deploy (dengan username yang benar)
.\deploy_simple.ps1 -PiIP "192.168.0.108" -PiUser "entung"

# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Copy file manual
scp file.txt entung@192.168.0.108:~/
```

---

**Masukkan password di terminal untuk melanjutkan deployment!** 🚀
