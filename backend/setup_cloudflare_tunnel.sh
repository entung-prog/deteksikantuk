#!/bin/bash
# Cloudflare Tunnel Setup Script
# Run this on Raspberry Pi after git pull

echo "======================================"
echo "🌐 Cloudflare Tunnel Setup"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -d "/home/entung" ]; then
    echo "❌ Error: This script must run on Raspberry Pi"
    exit 1
fi

echo "📦 Step 1: Installing cloudflared..."
echo ""

# Download cloudflared
if [ ! -f "/usr/local/bin/cloudflared" ]; then
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
    sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
    sudo chmod +x /usr/local/bin/cloudflared
    echo "✅ cloudflared installed"
else
    echo "✅ cloudflared already installed"
fi

# Verify installation
cloudflared --version
echo ""

echo "======================================"
echo "🔑 Step 2: Login to Cloudflare"
echo "======================================"
echo ""
echo "A browser window will open (or you'll get a URL)"
echo "1. Copy the URL"
echo "2. Open it in your laptop browser"
echo "3. Login to Cloudflare"
echo "4. Authorize cloudflared"
echo ""
read -p "Press Enter to continue..."

cloudflared tunnel login

if [ ! -f "$HOME/.cloudflared/cert.pem" ]; then
    echo "❌ Login failed. Please try again."
    exit 1
fi

echo ""
echo "✅ Successfully logged in to Cloudflare"
echo ""

echo "======================================"
echo "🚇 Step 3: Creating Tunnel"
echo "======================================"
echo ""

# Create tunnel
cloudflared tunnel create drowsiness-pi

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep drowsiness-pi | awk '{print $1}')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Failed to create tunnel"
    exit 1
fi

echo ""
echo "✅ Tunnel created!"
echo "📝 Tunnel ID: $TUNNEL_ID"
echo ""

echo "======================================"
echo "🌐 Step 4: Setting up DNS"
echo "======================================"
echo ""

# Setup DNS routes
cloudflared tunnel route dns drowsiness-pi api-drowsiness
cloudflared tunnel route dns drowsiness-pi camera-drowsiness

echo ""
echo "✅ DNS routes configured"
echo ""
echo "Your URLs:"
echo "  Backend API:    https://api-drowsiness.$TUNNEL_ID.cfargotunnel.com"
echo "  Camera Stream:  https://camera-drowsiness.$TUNNEL_ID.cfargotunnel.com"
echo ""

echo "======================================"
echo "⚙️  Step 5: Creating Config File"
echo "======================================"
echo ""

# Create config directory
mkdir -p ~/.cloudflared

# Create config file
cat > ~/.cloudflared/config.yml <<EOF
tunnel: $TUNNEL_ID
credentials-file: /home/entung/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: api-drowsiness.$TUNNEL_ID.cfargotunnel.com
    service: http://localhost:5001
  
  - hostname: camera-drowsiness.$TUNNEL_ID.cfargotunnel.com
    service: http://localhost:8080
  
  - service: http_status:404
EOF

echo "✅ Config file created at ~/.cloudflared/config.yml"
echo ""

echo "======================================"
echo "🧪 Step 6: Testing Tunnel"
echo "======================================"
echo ""
echo "Starting tunnel in test mode..."
echo "Press Ctrl+C to stop after testing"
echo ""

# Test tunnel
cloudflared tunnel run drowsiness-pi &
TUNNEL_PID=$!

sleep 5

echo ""
echo "Testing endpoints..."
curl -s https://api-drowsiness.$TUNNEL_ID.cfargotunnel.com/api/health || echo "⚠️  Backend not running (this is OK for now)"
echo ""

# Stop test tunnel
kill $TUNNEL_PID 2>/dev/null

echo "======================================"
echo "🔧 Step 7: Installing as Service"
echo "======================================"
echo ""

sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

echo "✅ Cloudflared service installed and started"
echo ""

echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "📋 Summary:"
echo "  Tunnel ID:      $TUNNEL_ID"
echo "  Backend API:    https://api-drowsiness.$TUNNEL_ID.cfargotunnel.com"
echo "  Camera Stream:  https://camera-drowsiness.$TUNNEL_ID.cfargotunnel.com"
echo ""
echo "📝 Save these URLs! You'll need them for Vercel configuration."
echo ""
echo "🔍 Check tunnel status:"
echo "  sudo systemctl status cloudflared"
echo ""
echo "📊 View logs:"
echo "  sudo journalctl -u cloudflared -f"
echo ""
echo "======================================"
