# 🌐 Cara Cek dan Setup Network di Raspberry Pi

## ❌ Masalah: hostname -I menunjukkan 127.0.1.1

Ini berarti Raspberry Pi **belum terhubung ke network** atau belum dapat IP address dari router.

---

## ✅ Solusi: Cek Network Connection

### **Step 1: Cek Interface Network**

Di Raspberry Pi, jalankan:

```bash
ip addr show
```

atau

```bash
ifconfig
```

Cari interface:
- **eth0** = Ethernet (kabel)
- **wlan0** = WiFi

### **Step 2: Cek Status Network**

```bash
# Cek semua IP address (termasuk network IP)
hostname -I

# Cek interface spesifik
ip addr show eth0    # untuk ethernet
ip addr show wlan0   # untuk wifi
```

---

## 🔌 Setup Ethernet (Kabel)

### **Cek kabel terpasang:**

```bash
# Cek link status
ip link show eth0

# Harus muncul: state UP
```

### **Jika eth0 DOWN:**

```bash
# Nyalakan interface
sudo ip link set eth0 up

# Restart networking
sudo systemctl restart dhcpcd
```

### **Request IP dari DHCP:**

```bash
# Restart DHCP client
sudo dhcpcd eth0

# Tunggu beberapa detik, lalu cek lagi
hostname -I
```

---

## 📡 Setup WiFi

### **Scan WiFi Networks:**

```bash
sudo iwlist wlan0 scan | grep ESSID
```

### **Connect ke WiFi:**

```bash
# Edit wpa_supplicant config
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Tambahkan di akhir file:
network={
    ssid="NAMA_WIFI_ANDA"
    psk="PASSWORD_WIFI_ANDA"
}

# Save: Ctrl+O, Enter
# Exit: Ctrl+X
```

### **Restart WiFi:**

```bash
# Restart wpa_supplicant
sudo systemctl restart wpa_supplicant

# Atau restart networking
sudo systemctl restart dhcpcd

# Tunggu 10-20 detik, lalu cek
hostname -I
```

### **Alternatif - Menggunakan raspi-config:**

```bash
sudo raspi-config

# Pilih:
# 1. System Options
#   → S1 Wireless LAN
#     → Masukkan SSID (nama WiFi)
#     → Masukkan password
#   → Finish
```

---

## 🔍 Troubleshooting

### **Cek apakah sudah dapat IP:**

```bash
# Harus muncul IP selain 127.0.1.1
hostname -I

# Contoh output yang benar:
# 192.168.0.108 127.0.1.1
```

### **Cek routing:**

```bash
ip route show

# Harus ada default gateway
# default via 192.168.0.1 dev eth0
```

### **Test koneksi internet:**

```bash
ping -c 4 8.8.8.8
ping -c 4 google.com
```

### **Restart semua networking:**

```bash
sudo systemctl restart networking
sudo systemctl restart dhcpcd
sudo reboot
```

---

## 📝 Quick Commands

```bash
# Cek IP address
hostname -I
ip addr show

# Ethernet
sudo ip link set eth0 up
sudo dhcpcd eth0

# WiFi
sudo raspi-config  # → Wireless LAN
# atau
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Restart network
sudo systemctl restart dhcpcd
sudo reboot

# Verify
hostname -I  # Harus muncul 192.168.x.x
```

---

## 🎯 Setelah Dapat IP Address

Setelah `hostname -I` menunjukkan IP seperti `192.168.0.108`:

1. **Enable SSH** (jika belum):
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

2. **Test dari Windows**:
   ```powershell
   ping 192.168.0.108
   ssh pi@192.168.0.108
   ```

3. **Deploy aplikasi**:
   ```powershell
   .\deploy_simple.ps1 -PiIP "192.168.0.108"
   ```

---

## ⚡ Quick Fix

Coba command ini di Raspberry Pi:

```bash
# Restart networking
sudo systemctl restart dhcpcd
sleep 5
hostname -I

# Jika masih 127.0.1.1, coba reboot
sudo reboot
```

Setelah reboot, login lagi dan cek:
```bash
hostname -I
```

Seharusnya muncul IP network (192.168.x.x atau 10.x.x.x)
