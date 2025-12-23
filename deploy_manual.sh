#!/bin/bash
# Manual Deployment Script - Run this directly on Raspberry Pi
# Copy this script content to Raspberry Pi and execute

echo "=========================================="
echo "Drowsiness Detection - Manual Deployment"
echo "=========================================="
echo ""

# Set variables
APP_DIR="/home/pi/drowsiness-detection"
SERVICE_NAME="drowsiness-backend"
WEB_SERVICE_NAME="drowsiness-web"

echo "[1/8] Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

echo ""
echo "[2/8] Please transfer these files to $APP_DIR:"
echo "  - backend_server.py"
echo "  - drowsiness_test.html"
echo "  - drowsiness_test.css"
echo "  - drowsiness_test_hybrid.js"
echo "  - requirements.txt"
echo "  - best_model.h5"
echo ""
echo "Press Enter when files are ready..."
read

# Check if files exist
echo "[3/8] Checking files..."
FILES=("backend_server.py" "drowsiness_test.html" "drowsiness_test.css" "drowsiness_test_hybrid.js" "requirements.txt" "best_model.h5")
MISSING=0

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file - MISSING"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "Error: Some files are missing. Please copy all files first."
    exit 1
fi

echo ""
echo "[4/8] Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt-get install -y libopencv-dev python3-opencv

echo ""
echo "[5/8] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[6/8] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[7/8] Setting up systemd services..."

# Create backend service
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Drowsiness Detection Backend Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python backend_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create web server service
sudo tee /etc/systemd/system/${WEB_SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Drowsiness Detection Web Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 -m http.server 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "[8/8] Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl enable ${WEB_SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}
sudo systemctl start ${WEB_SERVICE_NAME}

sleep 2

echo ""
echo "=========================================="
echo "Deployment Complete! ✅"
echo "=========================================="
echo ""
echo "Services are running:"
echo "  - Backend: http://localhost:5000"
echo "  - Web UI:  http://localhost:8000/drowsiness_test.html"
echo ""
echo "To access from another device:"
echo "  - Find Pi IP: hostname -I"
echo "  - Access: http://<pi-ip>:8000/drowsiness_test.html"
echo ""
echo "Check status:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo systemctl status ${WEB_SERVICE_NAME}"
echo ""
