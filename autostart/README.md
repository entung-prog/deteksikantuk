# Auto-Start Setup - Drowsiness Detection System

Folder ini berisi script dan dokumentasi untuk setup auto-start sistem deteksi kantuk di Raspberry Pi.

## 🚀 Quick Start

### 1. Jalankan Setup Script

```bash
cd /home/entung/deteksikantuk/autostart
chmod +x setup_autostart.sh
./setup_autostart.sh
```

Script akan otomatis:
- ✅ Membuat systemd service
- ✅ Enable auto-start on boot
- ✅ Start service
- ✅ Setup logging

### 2. Verifikasi

```bash
# Check service status
sudo systemctl status drowsiness

# Check logs
sudo journalctl -u drowsiness -f
```

---

## 📋 Service Management

### Start/Stop/Restart

```bash
# Start service
sudo systemctl start drowsiness

# Stop service
sudo systemctl stop drowsiness

# Restart service
sudo systemctl restart drowsiness

# Check status
sudo systemctl status drowsiness
```

### Enable/Disable Auto-start

```bash
# Enable auto-start on boot
sudo systemctl enable drowsiness

# Disable auto-start
sudo systemctl disable drowsiness

# Check if enabled
sudo systemctl is-enabled drowsiness
```

---

## 📊 Monitoring & Logs

### Real-time Logs

```bash
# System journal (recommended)
sudo journalctl -u drowsiness -f

# Last 100 lines
sudo journalctl -u drowsiness -n 100
```

### Log Files

```bash
# Application log
tail -f /var/log/drowsiness/drowsiness.log

# Error log
tail -f /var/log/drowsiness/drowsiness-error.log

# Search for alarms
grep "ALARM" /var/log/drowsiness/drowsiness.log
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check detailed status
sudo systemctl status drowsiness -l

# Check logs for errors
sudo journalctl -u drowsiness -n 50

# Test manually
cd /home/entung/deteksikantuk/backend
source venv/bin/activate
python3 app.py
```

### Common Issues

#### 1. Camera Not Found

**Error:** `Failed to initialize camera`

**Solution:**
```bash
# Check camera
ls /dev/video*

# Test camera
v4l2-ctl --list-devices

# Restart service
sudo systemctl restart drowsiness
```

#### 2. GPIO Permission Denied

**Error:** `Permission denied: /dev/gpiomem`

**Solution:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio entung

# Reboot
sudo reboot
```

#### 3. Port Already in Use

**Error:** `Address already in use: 5000`

**Solution:**
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Restart service
sudo systemctl restart drowsiness
```

---

## 🧪 Testing Auto-Start

### Test Reboot

```bash
# Reboot Pi
sudo reboot

# After reboot, check service
sudo systemctl status drowsiness

# Check if running
curl http://localhost:5000/health
```

### Simulate Failure

```bash
# Kill service
sudo systemctl kill drowsiness

# Service should auto-restart in 10 seconds
sleep 15
sudo systemctl status drowsiness
```

---

## 🗑️ Uninstall

### Remove Auto-Start

```bash
# Stop service
sudo systemctl stop drowsiness

# Disable auto-start
sudo systemctl disable drowsiness

# Remove service file
sudo rm /etc/systemd/system/drowsiness.service

# Reload systemd
sudo systemctl daemon-reload
```

---

## ✅ Production Checklist

Before deploying to car:

- [ ] Auto-start enabled and tested
- [ ] Hardware (buzzer + LEDs) connected and tested
- [ ] Camera positioned correctly
- [ ] Power supply stable (car USB charger)
- [ ] Logs rotating properly
- [ ] GPIO permissions configured
- [ ] Web interface accessible (for debugging)
- [ ] Reboot test passed
- [ ] Failure recovery tested

---

## 🌐 Remote Access

### Web Interface

Access from any device on same network:

```
http://192.168.x.x:5000
```

### USB Tethering

1. Connect Pi to phone via USB
2. Enable USB tethering on phone
3. Pi will get IP (e.g., 192.168.42.129)
4. Access web UI: `http://192.168.42.129:5000`

---

## 📝 What Gets Created

### Systemd Service

- **Location:** `/etc/systemd/system/drowsiness.service`
- **User:** entung
- **Working Directory:** `/home/entung/deteksikantuk/backend`
- **Auto-restart:** Yes (10 seconds delay)

### Log Files

- **Directory:** `/var/log/drowsiness/`
- **Application Log:** `drowsiness.log`
- **Error Log:** `drowsiness-error.log`

---

## 🎯 Status: Ready to Deploy!

System will automatically start on every boot and restart on failure.
