# Backend - Drowsiness Detection

Deploy folder ini ke Raspberry Pi.

## 📦 Files

- `backend_server.py` - Flask backend API
- `hardware_alert.py` - GPIO control (buzzer + LED)
- `camera_stream.py` - Camera streaming server
- `best_model.tflite` - TFLite INT8 model
- `requirements.txt` - Python dependencies
- `drowsiness-backend.service` - Systemd service (backend)
- `drowsiness-camera.service` - Systemd service (camera)
- `setup_autostart.sh` - Auto-start setup script
- `cloudflare-tunnel-config.yml` - Cloudflare Tunnel config

## 🚀 Setup on Raspberry Pi

```bash
# Copy folder ke Raspberry Pi
scp -r backend/ entung@192.168.0.108:~/deteksikantuk/

# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Install dependencies
cd ~/deteksikantuk/backend
pip install -r requirements.txt

# Run backend
python backend_server.py
```

## 🔧 Auto-Start

```bash
cd ~/deteksikantuk/backend
chmod +x setup_autostart.sh
./setup_autostart.sh
```

## 📖 Full Guides

- [Cloudflare Tunnel Setup](../docs/CLOUDFLARE_TUNNEL.md)
- [Hardware Setup](../docs/HARDWARE_SETUP.md)
- [Auto-Start Setup](../docs/AUTOSTART_SETUP.md)
