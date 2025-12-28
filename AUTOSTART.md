# Auto-Start Setup - Drowsiness Detection System

## Overview

Panduan lengkap untuk setup auto-start sistem deteksi kantuk di Raspberry Pi menggunakan systemd.

---

## Quick Start

### 1. Jalankan Setup Script

```bash
cd /home/entung/deteksikantuk
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

## Manual Setup (Alternative)

Jika ingin setup manual:

### Step 1: Create Service File

```bash
sudo nano /etc/systemd/system/drowsiness.service
```

Paste konfigurasi berikut:

```ini
[Unit]
Description=Drowsiness Detection System
After=network.target

[Service]
Type=simple
User=entung
WorkingDirectory=/home/entung/deteksikantuk/backend
Environment="PATH=/home/entung/deteksikantuk/backend/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/entung/deteksikantuk/backend/venv/bin/python3 /home/entung/deteksikantuk/backend/app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/drowsiness/drowsiness.log
StandardError=append:/var/log/drowsiness/drowsiness-error.log
SyslogIdentifier=drowsiness

[Install]
WantedBy=multi-user.target
```

### Step 2: Create Log Directory

```bash
sudo mkdir -p /var/log/drowsiness
sudo chown entung:entung /var/log/drowsiness
```

### Step 3: Enable & Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable drowsiness.service

# Start service
sudo systemctl start drowsiness.service

# Check status
sudo systemctl status drowsiness.service
```

---

## Service Management

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

## Monitoring & Logs

### Real-time Logs

```bash
# System journal (recommended)
sudo journalctl -u drowsiness -f

# Follow all logs
sudo journalctl -u drowsiness -f --all

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

# Count detections today
grep "$(date +%Y-%m-%d)" /var/log/drowsiness/drowsiness.log | grep "ALARM" | wc -l
```

### Log Rotation

Create log rotation config:

```bash
sudo nano /etc/logrotate.d/drowsiness
```

```
/var/log/drowsiness/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 entung entung
}
```

---

## Boot Sequence

### What Happens on Boot

1. **System boots** → Raspberry Pi starts
2. **Network ready** → Wait for network (if needed)
3. **Service starts** → drowsiness.service launches
4. **Camera init** → USB camera detected
5. **Model loads** → TFLite model loaded
6. **GPIO ready** → Hardware initialized
7. **Web server** → Flask running on port 5000
8. **System ready** → Green LED indicates ready state

**Total boot time:** ~30-60 seconds

### Boot Status Indicators

| LED Status | Meaning |
|------------|---------|
| All OFF | System booting |
| Green ON | System ready, alert state |
| Yellow ON | Warning (drowsy 0-3s) |
| Red ON + Buzzer | Alarm (drowsy ≥3s) |

---

## Troubleshooting

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

#### 4. Model Not Found

**Error:** `Model file not found`

**Solution:**
```bash
# Check model exists
ls -lh /home/entung/deteksikantuk/backend/*.tflite

# Verify path in service
sudo systemctl cat drowsiness
```

---

## Performance Tuning

### Reduce Boot Time

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups

# Optimize boot
sudo systemctl mask plymouth-quit-wait.service
```

### Memory Optimization

Add to `/boot/config.txt`:

```ini
# Reduce GPU memory (more for CPU)
gpu_mem=128

# Disable camera LED
disable_camera_led=1
```

### CPU Governor

```bash
# Set performance mode
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

---

## Remote Access

### SSH Access

```bash
# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Connect from laptop/phone
ssh entung@192.168.x.x
```

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

## Testing Auto-Start

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

## Uninstall

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

### Keep Logs

Logs will remain in `/var/log/drowsiness/` unless manually deleted.

---

## Production Checklist

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

## Monitoring Dashboard (Optional)

Create simple status check script:

```bash
nano ~/check_drowsiness.sh
```

```bash
#!/bin/bash
echo "Drowsiness Detection System Status"
echo "===================================="
echo ""
echo "Service Status:"
systemctl is-active drowsiness && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "Uptime:"
systemctl show drowsiness --property=ActiveEnterTimestamp --value
echo ""
echo "Recent Alarms:"
grep "ALARM" /var/log/drowsiness/drowsiness.log | tail -5
echo ""
echo "Web Interface:"
curl -s http://localhost:5000/health | jq .
```

```bash
chmod +x ~/check_drowsiness.sh
```

---

## Status: ✅ Auto-Start Ready!

System will automatically start on every boot and restart on failure.
