#!/bin/bash
# Auto-Start Setup Script for Drowsiness Detection System
# Run this script on Raspberry Pi to enable auto-start on boot

echo "======================================"
echo "🚀 Drowsiness Detection Auto-Start"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -d "/home/entung/deteksikantuk" ]; then
    echo "❌ Error: /home/entung/deteksikantuk not found"
    echo "   Please run this script on Raspberry Pi"
    exit 1
fi

cd /home/entung/deteksikantuk

echo "📦 Step 1: Copying service files..."
sudo cp drowsiness-backend.service /etc/systemd/system/
sudo cp drowsiness-camera.service /etc/systemd/system/

echo "✅ Service files copied"
echo ""

echo "🔄 Step 2: Reloading systemd..."
sudo systemctl daemon-reload

echo "✅ Systemd reloaded"
echo ""

echo "🔧 Step 3: Enabling services..."
sudo systemctl enable drowsiness-backend.service
sudo systemctl enable drowsiness-camera.service

echo "✅ Services enabled"
echo ""

echo "▶️  Step 4: Starting services..."
sudo systemctl start drowsiness-backend.service
sudo systemctl start drowsiness-camera.service

echo "✅ Services started"
echo ""

echo "======================================"
echo "✅ Auto-Start Setup Complete!"
echo "======================================"
echo ""
echo "📊 Service Status:"
echo ""
sudo systemctl status drowsiness-backend.service --no-pager -l
echo ""
sudo systemctl status drowsiness-camera.service --no-pager -l
echo ""

echo "======================================"
echo "💡 Useful Commands:"
echo "======================================"
echo ""
echo "Check status:"
echo "  sudo systemctl status drowsiness-backend"
echo "  sudo systemctl status drowsiness-camera"
echo ""
echo "View logs:"
echo "  sudo journalctl -u drowsiness-backend -f"
echo "  sudo journalctl -u drowsiness-camera -f"
echo ""
echo "Stop services:"
echo "  sudo systemctl stop drowsiness-backend"
echo "  sudo systemctl stop drowsiness-camera"
echo ""
echo "Restart services:"
echo "  sudo systemctl restart drowsiness-backend"
echo "  sudo systemctl restart drowsiness-camera"
echo ""
echo "Disable auto-start:"
echo "  sudo systemctl disable drowsiness-backend"
echo "  sudo systemctl disable drowsiness-camera"
echo ""
echo "======================================"
echo "🎉 System will now auto-start on boot!"
echo "======================================"
