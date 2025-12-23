#!/bin/bash
# Quick SSH Setup Script for Raspberry Pi
# Run this script on Raspberry Pi to enable and configure SSH

echo "=========================================="
echo "SSH Setup Script for Raspberry Pi"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root (don't use sudo)"
    exit 1
fi

echo "[1/5] Enabling SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

echo ""
echo "[2/5] Checking SSH status..."
if sudo systemctl is-active --quiet ssh; then
    echo "✓ SSH is running"
else
    echo "✗ SSH failed to start"
    exit 1
fi

echo ""
echo "[3/5] Configuring SSH..."
# Backup original config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Enable key authentication
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/PubkeyAuthentication no/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Restart SSH to apply changes
sudo systemctl restart ssh

echo ""
echo "[4/5] Getting network information..."
echo "IP Address(es):"
hostname -I
echo ""
echo "Hostname:"
hostname
echo ""

echo "[5/5] Checking firewall..."
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo "Firewall is active, allowing SSH..."
        sudo ufw allow 22
    else
        echo "Firewall is inactive"
    fi
else
    echo "UFW not installed (firewall disabled)"
fi

echo ""
echo "=========================================="
echo "SSH Setup Complete! ✅"
echo "=========================================="
echo ""
echo "SSH is now enabled and running"
echo ""
echo "Connection details:"
echo "  IP Address: $(hostname -I | awk '{print $1}')"
echo "  Username: $USER"
echo "  Port: 22"
echo ""
echo "Connect from Windows:"
echo "  ssh $USER@$(hostname -I | awk '{print $1}')"
echo ""
echo "Next steps:"
echo "  1. Change default password: passwd"
echo "  2. Setup SSH key for passwordless login"
echo "  3. Configure static IP (optional)"
echo ""
