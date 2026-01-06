#!/bin/bash
# Quick test script for GUI auto-detection mode

echo "=========================================="
echo "Testing GUI Auto-Detection Mode"
echo "=========================================="
echo ""
echo "This will:"
echo "  1. Check if display is available"
echo "  2. Test camera access"
echo "  3. Run app_auto_gui.py"
echo ""

# Check display
if [ -z "$DISPLAY" ]; then
    echo "⚠️  DISPLAY not set, setting to :0"
    export DISPLAY=:0
fi

echo "✅ DISPLAY=$DISPLAY"

# Check if we're in the right directory
if [ ! -f "app_auto_gui.py" ]; then
    echo "❌ app_auto_gui.py not found!"
    echo "   Please run this script from /home/entung/deteksikantuk/backend"
    exit 1
fi

# Check camera
echo ""
echo "Checking camera..."
if ls /dev/video* 1> /dev/null 2>&1; then
    echo "✅ Camera device(s) found:"
    ls -la /dev/video*
else
    echo "⚠️  No camera devices found at /dev/video*"
    echo "   Will try Pi Camera..."
fi

echo ""
echo "=========================================="
echo "Starting GUI Auto-Detection..."
echo "=========================================="
echo ""
echo "Controls:"
echo "  ESC   - Exit"
echo "  SPACE - Pause/Resume"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the application
python3 app_auto_gui.py
