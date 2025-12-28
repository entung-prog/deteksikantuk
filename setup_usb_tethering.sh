#!/bin/bash
# USB Tethering Setup for Raspberry Pi 5
# This enables direct USB connection between laptop and Raspberry Pi

echo "=========================================="
echo "USB Tethering Setup for Raspberry Pi"
echo "=========================================="
echo ""

# Backup files
echo "📦 Creating backups..."
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup
sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.backup

# Enable USB gadget mode in config.txt
echo "⚙️  Configuring USB gadget mode..."
if ! grep -q "dtoverlay=dwc2" /boot/firmware/config.txt; then
    echo "dtoverlay=dwc2" | sudo tee -a /boot/firmware/config.txt
    echo "✅ Added dtoverlay=dwc2 to config.txt"
else
    echo "✅ dtoverlay=dwc2 already exists in config.txt"
fi

# Enable USB ethernet gadget in cmdline.txt
echo "⚙️  Configuring USB ethernet gadget..."
CMDLINE=$(cat /boot/firmware/cmdline.txt)
if [[ ! $CMDLINE == *"modules-load=dwc2,g_ether"* ]]; then
    # Add after rootwait
    sudo sed -i 's/rootwait/rootwait modules-load=dwc2,g_ether/' /boot/firmware/cmdline.txt
    echo "✅ Added modules-load=dwc2,g_ether to cmdline.txt"
else
    echo "✅ modules-load already configured in cmdline.txt"
fi

# Configure static IP for usb0
echo "⚙️  Configuring static IP for USB interface..."
if ! grep -q "interface usb0" /etc/dhcpcd.conf; then
    cat << EOF | sudo tee -a /etc/dhcpcd.conf

# USB Tethering Configuration
interface usb0
static ip_address=192.168.7.2/24
static routers=192.168.7.1
static domain_name_servers=8.8.8.8
EOF
    echo "✅ Added USB network configuration to dhcpcd.conf"
else
    echo "✅ USB network already configured in dhcpcd.conf"
fi

# Install required packages
echo "📦 Installing required packages..."
sudo apt-get update
sudo apt-get install -y dnsmasq

echo ""
echo "=========================================="
echo "✅ USB Tethering Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo "1. Reboot Raspberry Pi: sudo reboot"
echo "2. Connect USB cable from Raspberry Pi to laptop"
echo "   (Use USB port, NOT the power port)"
echo "3. Raspberry Pi will appear as network device"
echo "4. Access web interface: http://192.168.7.2:5000"
echo "5. SSH access: ssh entung@192.168.7.2"
echo ""
echo "⚠️  IMPORTANT:"
echo "- Use a good quality USB-C cable"
echo "- Connect to USB port (not power port)"
echo "- On laptop, new network interface will appear"
echo ""
echo "🔄 Reboot now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Rebooting..."
    sudo reboot
else
    echo "Please reboot manually: sudo reboot"
fi
