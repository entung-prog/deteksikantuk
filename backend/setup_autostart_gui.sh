#!/bin/bash
# Setup autostart for GUI auto-detection mode
# This creates a desktop autostart entry

echo "=========================================="
echo "Setup Autostart - GUI Auto-Detection"
echo "=========================================="
echo ""

# Create autostart directory if it doesn't exist
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

# Create desktop entry
DESKTOP_FILE="$AUTOSTART_DIR/drowsiness-gui.desktop"

cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Type=Application
Name=Drowsiness Detection GUI
Comment=Auto-start drowsiness detection with camera preview
Exec=/usr/bin/python3 /home/entung/deteksikantuk/backend/app_auto_gui.py
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

echo "✅ Created desktop autostart entry:"
echo "   $DESKTOP_FILE"
echo ""
cat "$DESKTOP_FILE"
echo ""
echo "=========================================="
echo "Autostart Configuration Complete!"
echo "=========================================="
echo ""
echo "The drowsiness detection GUI will now start automatically"
echo "when you log in to the desktop."
echo ""
echo "To test without rebooting:"
echo "  cd /home/entung/deteksikantuk/backend"
echo "  ./test_gui_auto.sh"
echo ""
echo "To disable autostart:"
echo "  rm $DESKTOP_FILE"
echo ""
echo "To enable/disable via GUI:"
echo "  Open 'Startup Applications' or similar tool"
echo "  Look for 'Drowsiness Detection GUI'"
echo ""
