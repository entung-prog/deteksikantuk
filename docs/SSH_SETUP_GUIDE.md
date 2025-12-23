# 🔐 SSH Setup Guide - Raspberry Pi & Windows

Panduan lengkap untuk enable dan setup SSH di Raspberry Pi, kemudian connect dari laptop Windows.

---

## 📋 Part 1: Enable SSH di Raspberry Pi

### Method 1: Via raspi-config (Recommended)

Jika Anda punya akses monitor + keyboard ke Raspberry Pi:

```bash
# Login ke Raspberry Pi
# Username default: pi
# Password default: raspberry

# Jalankan raspi-config
sudo raspi-config

# Navigate menu:
# 3. Interface Options
#   → I2. SSH
#     → Yes (Enable SSH)
#   → Finish
#   → Reboot? Yes

# Atau langsung via command:
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Method 2: Via Boot Partition (Tanpa Monitor)

Jika tidak punya monitor/keyboard:

1. **Matikan Raspberry Pi**
2. **Cabut SD card**, masukkan ke laptop Windows
3. **Buka drive "boot"** (muncul sebagai removable drive)
4. **Buat file kosong** bernama `ssh` (tanpa extension)
   - Buka Notepad
   - Save As → File name: `ssh` (tanpa .txt)
   - Save type: All Files
   - Save ke drive boot
5. **Eject SD card**, masukkan kembali ke Raspberry Pi
6. **Nyalakan Raspberry Pi**
7. **Tunggu 2-3 menit** untuk boot

### Method 3: Via Command Line (Jika sudah login)

```bash
# Enable SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# Verify SSH is running
sudo systemctl status ssh

# Should show: Active: active (running)
```

---

## 🌐 Part 2: Cari IP Address Raspberry Pi

### Di Raspberry Pi (jika punya akses):

```bash
# Method 1: hostname command
hostname -I

# Method 2: ip command
ip addr show

# Method 3: ifconfig (jika tersedia)
ifconfig
```

### Dari Windows (scan network):

**Opsi A - Menggunakan arp:**
```powershell
arp -a | Select-String "192.168"
```

**Opsi B - Menggunakan script scanner:**
```powershell
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
.\find_raspi.ps1
```

**Opsi C - Advanced IP Scanner:**
1. Download: https://www.advanced-ip-scanner.com/
2. Scan range: 192.168.0.1 - 192.168.0.254
3. Cari device "raspberrypi"

---

## 🔌 Part 3: Test SSH Connection dari Windows

### Test Basic Connection:

```powershell
# Format: ssh username@ip-address
ssh pi@192.168.0.108

# Jika pertama kali connect, akan muncul:
# "Are you sure you want to continue connecting (yes/no)?"
# Ketik: yes

# Masukkan password (default: raspberry)
```

### Troubleshooting Connection:

```powershell
# Test 1: Ping dulu
ping 192.168.0.108

# Test 2: Test SSH port
Test-NetConnection -ComputerName 192.168.0.108 -Port 22

# Test 3: SSH dengan verbose
ssh -v pi@192.168.0.108
```

---

## 🔒 Part 4: Security Setup (Recommended)

### 1. Ganti Password Default

**Di Raspberry Pi:**
```bash
# Ganti password user pi
passwd

# Masukkan password lama: raspberry
# Masukkan password baru (2x)
```

### 2. Setup SSH Key (No Password Login)

**Di Windows (PowerShell):**

```powershell
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Tekan Enter untuk default location: C:\Users\maula\.ssh\id_rsa
# Tekan Enter untuk no passphrase (atau buat passphrase)

# Copy public key ke Raspberry Pi
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh pi@192.168.0.108 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Masukkan password Raspberry Pi satu kali terakhir
```

**Test SSH tanpa password:**
```powershell
ssh pi@192.168.0.108
# Seharusnya langsung masuk tanpa diminta password
```

### 3. Disable Password Authentication (Optional, setelah SSH key works)

**Di Raspberry Pi:**
```bash
sudo nano /etc/ssh/sshd_config

# Cari dan ubah:
# PasswordAuthentication yes
# menjadi:
# PasswordAuthentication no

# Save: Ctrl+O, Enter
# Exit: Ctrl+X

# Restart SSH service
sudo systemctl restart ssh
```

---

## 🚀 Part 5: Connect & Deploy

### Quick SSH Commands:

```powershell
# Connect to Raspberry Pi
ssh pi@192.168.0.108

# Copy file to Raspberry Pi
scp file.txt pi@192.168.0.108:/home/pi/

# Copy folder to Raspberry Pi
scp -r folder/ pi@192.168.0.108:/home/pi/

# Run command on Raspberry Pi (without login)
ssh pi@192.168.0.108 "hostname -I"
```

### Deploy Application via SSH:

```powershell
# Method 1: Using deployment script
cd c:\Users\maula\OneDrive\Dokumen\skripsi\pipeline\webtest
.\deploy_simple.ps1 -PiIP "192.168.0.108"

# Method 2: Manual commands
ssh pi@192.168.0.108 "mkdir -p /home/pi/drowsiness-detection"
scp -r * pi@192.168.0.108:/home/pi/drowsiness-detection/
ssh pi@192.168.0.108 "cd /home/pi/drowsiness-detection && chmod +x deploy.sh && ./deploy.sh"
```

---

## 🔧 Common Issues & Solutions

### Issue 1: "Connection refused"

**Cause**: SSH service not running

**Solution**:
```bash
# Di Raspberry Pi
sudo systemctl start ssh
sudo systemctl enable ssh
```

### Issue 2: "Connection timeout"

**Cause**: Firewall blocking atau network issue

**Solution**:
```bash
# Di Raspberry Pi - check firewall
sudo ufw status

# If active, allow SSH
sudo ufw allow 22

# Check SSH is listening
sudo netstat -tlnp | grep :22
```

### Issue 3: "Permission denied (publickey)"

**Cause**: SSH key tidak ter-setup dengan benar

**Solution**:
```bash
# Di Raspberry Pi - check permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Check SSH config
sudo nano /etc/ssh/sshd_config
# Pastikan: PubkeyAuthentication yes
```

### Issue 4: "Host key verification failed"

**Cause**: SSH key berubah (Raspberry Pi di-reinstall)

**Solution**:
```powershell
# Di Windows - remove old key
ssh-keygen -R 192.168.0.108

# Connect lagi
ssh pi@192.168.0.108
```

---

## 📱 Part 6: Setup Static IP (Recommended)

Agar IP tidak berubah-ubah:

**Di Raspberry Pi:**

```bash
# Edit dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Tambahkan di akhir file:
interface eth0  # atau wlan0 untuk WiFi
static ip_address=192.168.0.108/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1 8.8.8.8

# Save: Ctrl+O, Enter
# Exit: Ctrl+X

# Restart networking
sudo systemctl restart dhcpcd

# Reboot
sudo reboot
```

---

## ✅ Verification Checklist

- [ ] SSH enabled di Raspberry Pi
- [ ] SSH service running: `sudo systemctl status ssh`
- [ ] IP address diketahui: `hostname -I`
- [ ] Ping berhasil dari Windows: `ping 192.168.0.108`
- [ ] SSH connection berhasil: `ssh pi@192.168.0.108`
- [ ] Password sudah diganti dari default
- [ ] SSH key setup (optional)
- [ ] Static IP configured (optional)

---

## 🎯 Quick Reference

```powershell
# Connect
ssh pi@192.168.0.108

# Copy file
scp file.txt pi@192.168.0.108:~/

# Copy folder
scp -r folder/ pi@192.168.0.108:~/

# Run command
ssh pi@192.168.0.108 "command"

# Deploy app
.\deploy_simple.ps1 -PiIP "192.168.0.108"
```

---

**Setelah SSH setup berhasil, Anda bisa deploy aplikasi dengan mudah menggunakan script yang sudah saya buat!** 🚀
