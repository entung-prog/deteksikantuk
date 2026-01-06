# Drowsiness Detection System - Application Versions

## Overview
This project contains **4 different versions** of the drowsiness detection application, each designed for different use cases.

## 📁 Available Versions

### 1. `app.py` - Manual Testing Version
**Purpose**: Development and manual testing

**Features**:
- ✅ Web-based GUI (Flask)
- ✅ Camera preview in browser
- ✅ Manual detection (button press required)
- ✅ Bounding boxes for face and eyes
- ✅ LED indicators and statistics
- ✅ Export test results

**When to use**: Testing, development, demonstrations

**How to run**:
```bash
python3 app.py
# Open browser: http://localhost:5000
```

---

### 2. `app_auto.py` - Web Auto-Detection
**Purpose**: Remote monitoring with web interface

**Features**:
- ✅ Web-based GUI (Flask)
- ✅ Camera preview in browser
- ✅ **Automatic detection** (no button needed)
- ✅ Bounding boxes for face and eyes
- ✅ LED indicators and statistics
- ✅ Real-time status updates

**When to use**: Remote access, monitoring from another device, headless Pi with remote access

**How to run**:
```bash
python3 app_auto.py
# Open browser: http://localhost:5000
# Or from another device: http://<raspberry-pi-ip>:5000
```

---

### 3. `app_auto_cli.py` - Headless CLI Version
**Purpose**: Minimal resource usage, no display needed

**Features**:
- ✅ Terminal-only output
- ✅ **Automatic detection**
- ✅ Hardware GPIO support (LED + buzzer)
- ✅ Statistics tracking
- ❌ No camera preview
- ❌ No web interface

**When to use**: Headless Raspberry Pi, minimal resources, production deployment without display

**How to run**:
```bash
python3 app_auto_cli.py
# Or use the helper script:
./test_cli_auto.sh
```

---

### 4. `app_auto_gui.py` - GUI Window Version ⭐ **NEW!**
**Purpose**: Local monitoring with visual feedback

**Features**:
- ✅ **OpenCV GUI window** (not web browser)
- ✅ **Camera preview with bounding boxes**
- ✅ **Automatic detection**
- ✅ Real-time status overlay
- ✅ Visual LED indicators on screen
- ✅ Hardware GPIO support
- ✅ Statistics and FPS counter
- ✅ Keyboard controls (ESC, SPACE)
- ❌ Requires display connected

**When to use**: Raspberry Pi with display, local monitoring, in-car deployment with screen

**How to run**:
```bash
python3 app_auto_gui.py
# Or use the helper script:
./test_gui_auto.sh
```

**Documentation**: See [GUI_AUTO_README.md](GUI_AUTO_README.md)

---

## 📊 Comparison Table

| Feature | app.py | app_auto.py | app_auto_cli.py | app_auto_gui.py |
|---------|--------|-------------|-----------------|-----------------|
| **Interface** | Web Browser | Web Browser | Terminal | GUI Window |
| **Auto-Detection** | ❌ Manual | ✅ Yes | ✅ Yes | ✅ Yes |
| **Camera Preview** | ✅ Web | ✅ Web | ❌ No | ✅ OpenCV Window |
| **Bounding Boxes** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **LED Indicators** | ✅ Visual | ✅ Visual | ⚠️ Hardware only | ✅ Visual + Hardware |
| **Remote Access** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Display Required** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Resource Usage** | Medium | Medium | Low | Medium |
| **Best For** | Testing | Remote monitoring | Headless | Local monitoring |

---

## 🚀 Quick Start Guide

### For Testing
```bash
python3 app.py
# Open browser and click "Start Detection"
```

### For Remote Monitoring
```bash
python3 app_auto.py
# Access from any device on network
```

### For Headless Operation
```bash
python3 app_auto_cli.py
# Runs in background, no display needed
```

### For Local Monitoring with Display
```bash
python3 app_auto_gui.py
# Shows camera preview window
```

---

## 🔧 Setup for Autostart

### Web Version (Remote Access)
```bash
cd /home/entung/deteksikantuk/autostart
./setup_autostart_auto.sh
```

### CLI Version (Headless)
```bash
# Edit the service file to use app_auto_cli.py
sudo nano /etc/systemd/system/drowsiness_auto.service
# Change ExecStart line to: python3 app_auto_cli.py
```

### GUI Version (With Display)
```bash
cd /home/entung/deteksikantuk/backend
./setup_autostart_gui.sh
```

---

## 📖 Documentation

- **General Setup**: [../README.md](../README.md)
- **GPIO Configuration**: [GPIO_SETUP.md](GPIO_SETUP.md)
- **CLI Version**: [CLI_AUTO_README.md](CLI_AUTO_README.md)
- **GUI Version**: [GUI_AUTO_README.md](GUI_AUTO_README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Testing Guide**: [testing_guide.md](testing_guide.md)

---

## 🎯 Use Case Recommendations

### In-Car Deployment
- **With display**: Use `app_auto_gui.py` - shows camera and status on screen
- **Without display**: Use `app_auto_cli.py` - minimal resources, hardware alerts only

### Development/Testing
- Use `app.py` - manual control, easy testing

### Remote Monitoring
- Use `app_auto.py` - access from phone/laptop via web browser

### Production (Headless)
- Use `app_auto_cli.py` - lowest resource usage, reliable

### Demonstration/Presentation
- Use `app_auto_gui.py` - best visual feedback

---

## 🔋 Performance Comparison

### Raspberry Pi 4 (4GB)

| Version | FPS | CPU Usage | RAM Usage |
|---------|-----|-----------|-----------|
| app.py | 15-20 | 50-60% | ~200MB |
| app_auto.py | 15-20 | 50-60% | ~200MB |
| app_auto_cli.py | 10-15 | 30-40% | ~150MB |
| app_auto_gui.py | 20-30 | 40-60% | ~180MB |

### Raspberry Pi 3B+

| Version | FPS | CPU Usage | RAM Usage |
|---------|-----|-----------|-----------|
| app.py | 8-12 | 70-80% | ~180MB |
| app_auto.py | 8-12 | 70-80% | ~180MB |
| app_auto_cli.py | 8-10 | 50-60% | ~120MB |
| app_auto_gui.py | 10-15 | 70-90% | ~160MB |

---

## 🛠️ Common Tasks

### Switch Between Versions
Just run the appropriate Python file - they don't interfere with each other.

### Test All Versions
```bash
# Test manual version
python3 app.py

# Test web auto version
python3 app_auto.py

# Test CLI version
python3 app_auto_cli.py

# Test GUI version
python3 app_auto_gui.py
```

### Change Detection Threshold
Edit the file and change:
```python
drowsy_duration_threshold = 3.0  # seconds
```

### Change Confidence Threshold
Edit the file and change:
```python
predict_drowsiness(frame, threshold=0.65)  # 0.0-1.0
```

---

## 📝 Notes

- All versions use the same model: `best_model_compatible.tflite`
- All versions support the same GPIO pins (if available)
- All versions use the same face/eye detection cascades
- You can run different versions at different times (not simultaneously)

---

## 🆘 Support

For issues:
1. Check the appropriate README file for your version
2. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Verify camera and model files are present
4. Check GPIO connections (if using hardware)

---

## 📄 License

See main project README for license information.
