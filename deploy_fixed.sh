#!/bin/bash
# Fixed Deployment Script for Raspberry Pi (Updated for newer OS)
# This version removes deprecated packages

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
APP_DIR="/home/entung/drowsiness-detection"
SERVICE_NAME="drowsiness-backend"
WEB_SERVICE_NAME="drowsiness-web"

echo -e "${YELLOW}[1/8] Checking system requirements...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

echo -e "${GREEN}[2/8] Creating application directory...${NC}"
cd $APP_DIR

echo -e "${GREEN}[3/8] Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv python3-dev
sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
# Skip deprecated packages: libjasper-dev libqtgui4 libqt4-test
sudo apt-get install -y libopencv-dev python3-opencv

echo -e "${GREEN}[4/8] Creating Python virtual environment...${NC}"
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
User=entung
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
User=entung
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
echo "To access from your laptop:"
IP_ADDR=$(hostname -I | awk '{print $1}')
echo "  - Raspberry Pi IP: $IP_ADDR"
echo "  - Open browser on laptop: http://$IP_ADDR:8000/drowsiness_test.html"
echo ""
echo "Useful commands:"
echo "  - Check backend status: sudo systemctl status ${SERVICE_NAME}"
echo "  - Check web status:     sudo systemctl status ${WEB_SERVICE_NAME}"
echo "  - View backend logs:    sudo journalctl -u ${SERVICE_NAME} -f"
echo "  - Restart backend:      sudo systemctl restart ${SERVICE_NAME}"
echo ""
