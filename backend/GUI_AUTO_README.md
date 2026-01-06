# Drowsiness Detection - GUI Auto Mode

## Overview
This version displays camera preview in an **OpenCV GUI window** (not web browser) with real-time drowsiness detection. Perfect for autostart on boot with a connected display.

## Features
- ✅ **Camera Preview Window** - Direct OpenCV display (no web browser needed)
- ✅ **Real-time Bounding Boxes** - Face and eye detection visualization
- ✅ **Status Overlay** - ALERT/DROWSY/NO FACE with confidence and duration
- ✅ **LED Indicators** - Visual indicators on screen + hardware GPIO support
- ✅ **Statistics Display** - Total detections, drowsy count, alert count
- ✅ **Keyboard Controls** - ESC to exit, SPACE to pause/resume
- ✅ **Auto-Detection** - Continuous monitoring without button presses
- ✅ **FPS Counter** - Real-time performance monitoring

## Requirements

### System Requirements
- **Display/Monitor** - Must be connected (requires X11/desktop environment)
- **Python 3.7+**
- **OpenCV with GUI support** (`cv2.imshow` must work)
- **Camera** - USB webcam or Raspberry Pi Camera Module

### Python Dependencies
```bash
pip install opencv-python numpy
pip install tflite-runtime  # or tensorflow-lite
```

### Optional (for GPIO hardware alerts)
```bash
pip install gpiozero
```

## Usage

### Running Manually
```bash
cd /home/entung/deteksikantuk/backend
python3 app_auto_gui.py
```

### Keyboard Controls
- **ESC** - Exit application
- **SPACE** - Pause/Resume detection

### Display Layout
```
┌─────────────────────────────────────────────────────┐
│  [STATUS BADGE: ALERT/DROWSY/NO FACE]              │
│  Confidence: XX%                                    │
│  Duration: X.Xs (if drowsy)                        │
│                                                     │
│  ┌───────────────────────────────────────────┐     │
│  │                                           │     │
│  │   Camera Preview with Bounding Boxes     │     │
│  │   [Green Face Box]  [Cyan Eye Boxes]     │     │
│  │                                           │     │
│  └───────────────────────────────────────────┘     │
│                                                     │
│  LED Status: 🟢 Alert  🟡 Warning  🔴 Alarm        │
│  Total: XX | Drowsy: XX | Alert: XX               │
│  FPS: XX                                           │
│                                                     │
│  ESC: Exit | SPACE: Pause                          │
└─────────────────────────────────────────────────────┘
```

## LED States

### Visual Indicators (on screen)
- 🟢 **Green** - Alert (awake, eyes open)
- 🟡 **Yellow** - Warning (drowsy detected, duration < 3s)
- 🔴 **Red** - Alarm (drowsy duration ≥ 3s)
- ⚫ **Off** - No face detected

### Hardware GPIO (if available)
- **GPIO 27** - Green LED
- **GPIO 22** - Red LED  
- **GPIO 24** - Blue LED
- **GPIO 17** - Buzzer

The RGB LED creates:
- Green (0, 100, 0) - Alert
- Yellow (100, 100, 0) - Warning
- Red (100, 0, 0) - Alarm

## Autostart Setup

### Option 1: Using Existing Autostart Script
Edit `/home/entung/deteksikantuk/autostart/drowsiness_auto.service`:

```bash
# Change the ExecStart line to use app_auto_gui.py
ExecStart=/usr/bin/python3 /home/entung/deteksikantuk/backend/app_auto_gui.py

# Add environment variable for display
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/pi/.Xauthority"
```

### Option 2: Desktop Autostart (Recommended for GUI)
Create `~/.config/autostart/drowsiness-gui.desktop`:

```desktop
[Desktop Entry]
Type=Application
Name=Drowsiness Detection GUI
Exec=/usr/bin/python3 /home/entung/deteksikantuk/backend/app_auto_gui.py
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
```

### Option 3: Manual Autostart Script
Create a simple script:

```bash
#!/bin/bash
# Start drowsiness detection GUI on boot

export DISPLAY=:0
cd /home/entung/deteksikantuk/backend
python3 app_auto_gui.py
```

Save as `start_gui.sh`, make executable, and add to autostart.

## Troubleshooting

### Window Not Appearing
```bash
# Check if X11 is running
echo $DISPLAY
# Should output: :0 or :0.0

# Test OpenCV GUI
python3 -c "import cv2; cv2.namedWindow('test'); cv2.waitKey(1000)"
```

### "Can't open display" Error
```bash
# Set DISPLAY environment variable
export DISPLAY=:0

# Or for systemd service, add to service file:
Environment="DISPLAY=:0"
```

### Permission Denied for Display
```bash
# Allow X11 access (run as the user who started X)
xhost +local:

# Or set proper XAUTHORITY
export XAUTHORITY=/home/pi/.Xauthority
```

### Camera Not Found
```bash
# List available cameras
ls -la /dev/video*

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### Low FPS / Performance Issues
- Reduce window size (default 800x600)
- Lower camera resolution in code (default 640x480)
- Disable eye detection if not needed
- Run on Raspberry Pi 4 or better for best performance

## Comparison with Other Versions

| Feature | app.py | app_auto.py | app_auto_cli.py | app_auto_gui.py |
|---------|--------|-------------|-----------------|-----------------|
| Auto-detection | ❌ Manual | ✅ Yes | ✅ Yes | ✅ Yes |
| Camera Preview | ✅ Web | ✅ Web | ❌ No | ✅ GUI Window |
| Bounding Boxes | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| LED Indicators | ✅ Yes | ✅ Yes | ✅ Hardware only | ✅ Visual + Hardware |
| Web Server | ✅ Flask | ✅ Flask | ❌ No | ❌ No |
| Display Required | ❌ No | ❌ No | ❌ No | ✅ Yes |
| Best For | Testing | Remote monitoring | Headless | Local monitoring |

## Performance

### Raspberry Pi 4
- **FPS**: 20-30 FPS
- **CPU Usage**: 40-60%
- **Latency**: ~50ms

### Raspberry Pi 3
- **FPS**: 10-15 FPS
- **CPU Usage**: 70-90%
- **Latency**: ~100ms

## Tips

1. **For Best Performance**: Use Raspberry Pi 4 with 2GB+ RAM
2. **For Autostart**: Use desktop autostart method (Option 2)
3. **For Headless**: Use `app_auto_cli.py` instead
4. **For Remote**: Use `app_auto.py` (web interface)
5. **For Testing**: Run manually first to verify everything works

## Exit Codes
- **0** - Normal exit (ESC pressed)
- **1** - Camera initialization failed
- **2** - Model initialization failed
- **130** - Interrupted (Ctrl+C)

## Logs
The application prints status to stdout/stderr:
- ✅ Success messages (green)
- ⚠️  Warning messages (yellow)
- ❌ Error messages (red)

When running as a service, check logs with:
```bash
journalctl -u drowsiness_auto.service -f
```

## Support
For issues, check:
1. Camera is connected and working
2. Display is connected and X11 is running
3. Model file exists: `best_model_compatible.tflite`
4. OpenCV is installed with GUI support
5. Python dependencies are installed
