#!/bin/bash

# Quick Copy Script - Transfer files to Raspberry Pi
# Usage: ./copy_to_pi.sh <raspberry-pi-ip>

if [ -z "$1" ]; then
    echo "Usage: ./copy_to_pi.sh <raspberry-pi-ip>"
    echo "Example: ./copy_to_pi.sh 192.168.1.100"
    exit 1
fi

PI_IP=$1
PI_USER="pi"
TARGET_DIR="/home/pi/drowsiness-detection"

echo "=========================================="
echo "Copying files to Raspberry Pi: $PI_IP"
echo "=========================================="

# Create target directory on Pi
echo "[1/3] Creating directory on Raspberry Pi..."
ssh ${PI_USER}@${PI_IP} "mkdir -p ${TARGET_DIR}"

# Copy application files
echo "[2/3] Copying application files..."
scp backend_server.py ${PI_USER}@${PI_IP}:${TARGET_DIR}/
scp drowsiness_test.html ${PI_USER}@${PI_IP}:${TARGET_DIR}/
scp drowsiness_test.css ${PI_USER}@${PI_IP}:${TARGET_DIR}/
scp drowsiness_test_hybrid.js ${PI_USER}@${PI_IP}:${TARGET_DIR}/
scp requirements.txt ${PI_USER}@${PI_IP}:${TARGET_DIR}/
scp deploy.sh ${PI_USER}@${PI_IP}:${TARGET_DIR}/
scp README_DEPLOYMENT.md ${PI_USER}@${PI_IP}:${TARGET_DIR}/

# Copy model file (if exists)
if [ -f "../best_model.h5" ]; then
    echo "[3/3] Copying model file..."
    scp ../best_model.h5 ${PI_USER}@${PI_IP}:${TARGET_DIR}/
else
    echo "[3/3] Warning: best_model.h5 not found, skipping..."
fi

echo ""
echo "=========================================="
echo "Transfer Complete! ✅"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. SSH to Raspberry Pi:"
echo "   ssh ${PI_USER}@${PI_IP}"
echo ""
echo "2. Run deployment script:"
echo "   cd ${TARGET_DIR}"
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh"
echo ""
