#!/bin/bash

# Deployment Script for Raspberry Pi
# Drowsiness Detection Web Application

set -e  # Exit on error

echo "=========================================="
echo "Drowsiness Detection - Raspberry Pi Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/pi/drowsiness-detection"
SERVICE_NAME="drowsiness-backend"
WEB_SERVICE_NAME="drowsiness-web"

echo -e "${YELLOW}[1/8] Checking system requirements...${NC}"
# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo -e "${RED}Warning: This might not be a Raspberry Pi${NC}"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

echo -e "${GREEN}[2/8] Creating application directory...${NC}"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo -e "${GREEN}[3/8] Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt-get install -y libjasper-dev libqtgui4 libqt4-test
sudo apt-get install -y libopencv-dev python3-opencv

echo -e "${GREEN}[4/8] Creating Python virtual environment...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}[5/8] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}[6/8] Setting up systemd services...${NC}"

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

echo -e "${GREEN}[7/8] Enabling and starting services...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl enable ${WEB_SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}
sudo systemctl start ${WEB_SERVICE_NAME}

echo -e "${GREEN}[8/8] Checking service status...${NC}"
sleep 2
sudo systemctl status ${SERVICE_NAME} --no-pager
sudo systemctl status ${WEB_SERVICE_NAME} --no-pager

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete! ✅"
echo "==========================================${NC}"
echo ""
echo "Services are running:"
echo "  - Backend: http://localhost:5000"
echo "  - Web UI:  http://localhost:8000/drowsiness_test.html"
echo ""
echo "To access from another device on the network:"
echo "  - Find Raspberry Pi IP: hostname -I"
echo "  - Access: http://<raspberry-pi-ip>:8000/drowsiness_test.html"
echo ""
echo "Useful commands:"
echo "  - Check backend status: sudo systemctl status ${SERVICE_NAME}"
echo "  - Check web status:     sudo systemctl status ${WEB_SERVICE_NAME}"
echo "  - View backend logs:    sudo journalctl -u ${SERVICE_NAME} -f"
echo "  - View web logs:        sudo journalctl -u ${WEB_SERVICE_NAME} -f"
echo "  - Restart backend:      sudo systemctl restart ${SERVICE_NAME}"
echo "  - Restart web:          sudo systemctl restart ${WEB_SERVICE_NAME}"
echo ""
