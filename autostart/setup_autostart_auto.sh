#!/bin/bash
# Setup auto-start untuk Drowsiness Detection System (Auto Version) di Raspberry Pi

set -e

echo "=========================================="
echo "Auto-Start Setup - Auto Detection Version"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't look like a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_DIR="$PROJECT_DIR/backend"
VENV_PATH="$APP_DIR/venv"
APP_PATH="$APP_DIR/app_auto.py"
LOG_DIR="/var/log/drowsiness"

echo "📁 Project directory: $PROJECT_DIR"
echo "📁 Application directory: $APP_DIR"
echo "🐍 Virtual environment: $VENV_PATH"
echo "📝 Log directory: $LOG_DIR"
echo "🚀 Application: app_auto.py (Auto-Detection)"
echo ""

# Check if venv exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "Please create it first:"
    echo "  cd $APP_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if app_auto.py exists
if [ ! -f "$APP_PATH" ]; then
    echo "❌ app_auto.py not found at $APP_PATH"
    exit 1
fi

# Create log directory
echo "📝 Creating log directory..."
sudo mkdir -p $LOG_DIR
sudo chown $USER:$USER $LOG_DIR
echo "✅ Log directory created: $LOG_DIR"
echo ""

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/drowsiness-auto.service"
echo "📄 Creating systemd service file..."

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Drowsiness Detection System (Auto-Detection)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_PATH/bin/python3 $APP_PATH
Restart=always
RestartSec=10
StandardOutput=append:$LOG_DIR/drowsiness-auto.log
StandardError=append:$LOG_DIR/drowsiness-auto-error.log

# Logging
SyslogIdentifier=drowsiness-auto

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created: $SERVICE_FILE"
echo ""

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✅ Systemd reloaded"
echo ""

# Enable service
echo "🚀 Enabling auto-start on boot..."
sudo systemctl enable drowsiness-auto.service
echo "✅ Auto-start enabled"
echo ""

# Start service
echo "▶️  Starting service..."
sudo systemctl start drowsiness-auto.service
echo "✅ Service started"
echo ""

# Wait a moment for service to start
sleep 3

# Check status
echo "📊 Service status:"
echo "=========================================="
sudo systemctl status drowsiness-auto.service --no-pager
echo "=========================================="
echo ""

# Show useful commands
echo "✅ Setup complete!"
echo ""
echo "Useful commands:"
echo "  Start:   sudo systemctl start drowsiness-auto"
echo "  Stop:    sudo systemctl stop drowsiness-auto"
echo "  Restart: sudo systemctl restart drowsiness-auto"
echo "  Status:  sudo systemctl status drowsiness-auto"
echo "  Logs:    sudo journalctl -u drowsiness-auto -f"
echo "  Log file: tail -f $LOG_DIR/drowsiness-auto.log"
echo ""
echo "Web interface will be available at:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "🎉 Auto-Detection System will now start automatically on boot!"
echo "   No button press needed - detection starts immediately!"
echo ""
