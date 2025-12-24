# Auto-Start Setup Guide

## 🎯 Overview

Panduan untuk mengaktifkan auto-start sistem deteksi kantuk saat Raspberry Pi boot.

---

## 🚀 Quick Setup

### Di Raspberry Pi:

```bash
cd ~/deteksikantuk
git pull

# Jalankan setup script
chmod +x setup_autostart.sh
./setup_autostart.sh
```

Script akan otomatis:
1. ✅ Copy service files ke systemd
2. ✅ Enable auto-start
3. ✅ Start services
4. ✅ Show status

---

## 📋 Manual Setup (Jika Script Gagal)

### Step 1: Copy Service Files

```bash
cd ~/deteksikantuk
sudo cp drowsiness-backend.service /etc/systemd/system/
sudo cp drowsiness-camera.service /etc/systemd/system/
```

### Step 2: Reload Systemd

```bash
sudo systemctl daemon-reload
```

### Step 3: Enable Services

```bash
sudo systemctl enable drowsiness-backend.service
sudo systemctl enable drowsiness-camera.service
```

### Step 4: Start Services

```bash
sudo systemctl start drowsiness-backend.service
sudo systemctl start drowsiness-camera.service
```

### Step 5: Check Status

```bash
sudo systemctl status drowsiness-backend
sudo systemctl status drowsiness-camera
```

---

## 🔍 Service Details

### Backend Service (`drowsiness-backend.service`)

- **Runs:** `backend_server.py`
- **Port:** 5001
- **Auto-restart:** Yes (if crashed)
- **Starts after:** Network is ready

### Camera Service (`drowsiness-camera.service`)

- **Runs:** `camera_stream.py`
- **Port:** 8080
- **Auto-restart:** Yes (if crashed)
- **Starts after:** Network + Backend ready

---

## 💡 Useful Commands

### Check Status

```bash
# Backend status
sudo systemctl status drowsiness-backend

# Camera status
sudo systemctl status drowsiness-camera

# Both (short)
sudo systemctl status drowsiness-*
```

### View Logs (Real-time)

```bash
# Backend logs
sudo journalctl -u drowsiness-backend -f

# Camera logs
sudo journalctl -u drowsiness-camera -f

# Both logs
sudo journalctl -u drowsiness-* -f
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart drowsiness-backend

# Restart camera
sudo systemctl restart drowsiness-camera

# Restart both
sudo systemctl restart drowsiness-*
```

### Stop Services

```bash
# Stop backend
sudo systemctl stop drowsiness-backend

# Stop camera
sudo systemctl stop drowsiness-camera

# Stop both
sudo systemctl stop drowsiness-*
```

### Disable Auto-Start

```bash
# Disable backend
sudo systemctl disable drowsiness-backend

# Disable camera
sudo systemctl disable drowsiness-camera

# Disable both
sudo systemctl disable drowsiness-*
```

---

## 🔧 Troubleshooting

### Service Failed to Start

**Check logs:**
```bash
sudo journalctl -u drowsiness-backend -n 50
```

**Common issues:**
- Virtual environment not found → Check path in service file
- Permission denied → Check user in service file
- Port already in use → Kill existing process

### Service Not Auto-Starting on Boot

**Check if enabled:**
```bash
sudo systemctl is-enabled drowsiness-backend
sudo systemctl is-enabled drowsiness-camera
```

**Re-enable:**
```bash
sudo systemctl enable drowsiness-backend
sudo systemctl enable drowsiness-camera
```

### Hardware Not Working

**Check GPIO permissions:**
```bash
sudo usermod -a -G gpio entung
sudo reboot
```

---

## 📊 Testing Auto-Start

### Test 1: Reboot Test

```bash
# Reboot Raspberry Pi
sudo reboot

# Wait for boot...

# Check if services started
sudo systemctl status drowsiness-*

# Check if ports are open
curl http://localhost:5001/api/health
curl http://localhost:8080/health
```

### Test 2: Web Interface Test

```bash
# From laptop browser
http://192.168.0.108:8000/drowsiness_test.html
```

**Expected:**
- ✅ Backend responds
- ✅ Camera stream works
- ✅ Detection works
- ✅ Hardware alerts work

---

## ⚙️ Customization

### Change User

Edit service files:
```bash
sudo nano /etc/systemd/system/drowsiness-backend.service
```

Change line:
```
User=entung  # Change to your username
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart drowsiness-backend
```

### Change Working Directory

Edit service files:
```bash
WorkingDirectory=/home/entung/deteksikantuk  # Change path
```

### Add Environment Variables

Edit service files:
```bash
[Service]
Environment="DEBUG=1"
Environment="LOG_LEVEL=INFO"
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Services enabled: `systemctl is-enabled drowsiness-*`
- [ ] Services running: `systemctl status drowsiness-*`
- [ ] Backend responds: `curl http://localhost:5001/api/health`
- [ ] Camera responds: `curl http://localhost:8080/health`
- [ ] Web interface works from laptop
- [ ] Hardware alerts work (LED + buzzer)
- [ ] Auto-start after reboot works

---

## 🎉 Success!

Sistem sekarang akan otomatis start setiap kali Raspberry Pi boot!

**No more manual start!** 🚀
