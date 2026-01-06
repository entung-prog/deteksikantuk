#!/bin/bash
# Quick launcher for drowsiness detection apps
# Shows menu to choose which version to run

clear
echo "=========================================="
echo "🚗 Drowsiness Detection System"
echo "=========================================="
echo ""
echo "Choose version to run:"
echo ""
echo "  1) Manual Testing (Web GUI)"
echo "     - Browser interface"
echo "     - Manual start/stop"
echo "     - Best for: Testing"
echo ""
echo "  2) Auto Web (Web GUI)"
echo "     - Browser interface"
echo "     - Auto-detection"
echo "     - Best for: Remote monitoring"
echo ""
echo "  3) Auto CLI (Terminal)"
echo "     - Terminal output only"
echo "     - Auto-detection"
echo "     - Best for: Headless operation"
echo ""
echo "  4) Auto GUI (Window) ⭐ NEW!"
echo "     - OpenCV window preview"
echo "     - Auto-detection"
echo "     - Best for: Local monitoring"
echo ""
echo "  5) Exit"
echo ""
echo "=========================================="
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Starting Manual Testing Version..."
        echo "Open browser: http://localhost:5000"
        echo ""
        python3 app.py
        ;;
    2)
        echo ""
        echo "Starting Auto Web Version..."
        echo "Open browser: http://localhost:5000"
        echo ""
        python3 app_auto.py
        ;;
    3)
        echo ""
        echo "Starting Auto CLI Version..."
        echo "Press Ctrl+C to stop"
        echo ""
        python3 app_auto_cli.py
        ;;
    4)
        echo ""
        echo "Starting Auto GUI Version..."
        echo "Controls: ESC=Exit, SPACE=Pause"
        echo ""
        # Set DISPLAY if not set
        if [ -z "$DISPLAY" ]; then
            export DISPLAY=:0
        fi
        python3 app_auto_gui.py
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
