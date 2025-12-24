# Cloudflare Tunnel Setup Guide

## 🎯 Overview

Panduan lengkap setup Cloudflare Tunnel untuk expose Raspberry Pi backend ke internet dengan HTTPS gratis.

---

## 📋 Prerequisites

- Akun Cloudflare (gratis)
- Domain (opsional, bisa pakai subdomain Cloudflare gratis)
- Raspberry Pi dengan internet connection
- Backend dan camera stream sudah running

---

## 🚀 Setup Cloudflare Tunnel

### Step 1: Install cloudflared di Raspberry Pi

```bash
# SSH ke Raspberry Pi
ssh entung@192.168.0.108

# Download cloudflared untuk ARM64
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64

# Install
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Verify installation
cloudflared --version
```

Expected output: `cloudflared version 2024.x.x`

---

### Step 2: Login ke Cloudflare

```bash
cloudflared tunnel login
```

**Apa yang terjadi:**
1. Browser akan terbuka (atau akan muncul URL)
2. Login ke akun Cloudflare Anda
3. Pilih domain yang akan dipakai (atau buat baru)
4. Authorize cloudflared

**Output:**
```
You have successfully logged in.
Certificate saved to: /home/entung/.cloudflared/cert.pem
```

---

### Step 3: Create Tunnel

```bash
cloudflared tunnel create drowsiness-pi
```

**Output:**
```
Tunnel credentials written to /home/entung/.cloudflared/<TUNNEL-ID>.json
Created tunnel drowsiness-pi with id <TUNNEL-ID>
```

**PENTING:** Catat `<TUNNEL-ID>` ini! Anda akan butuh nanti.

---

### Step 4: Configure DNS

Anda perlu map 2 subdomain ke tunnel:

```bash
# Backend API
cloudflared tunnel route dns drowsiness-pi api-drowsiness.your-domain.com

# Camera Stream
cloudflared tunnel route dns drowsiness-pi camera-drowsiness.your-domain.com
```

**Ganti `your-domain.com` dengan:**
- Domain Anda sendiri (jika punya)
- Atau pakai subdomain gratis dari Cloudflare: `<tunnel-id>.cfargotunnel.com`

**Contoh dengan subdomain gratis:**
```bash
cloudflared tunnel route dns drowsiness-pi api-drowsiness
cloudflared tunnel route dns drowsiness-pi camera-drowsiness
```

Maka URL-nya akan jadi:
- `https://api-drowsiness.<tunnel-id>.cfargotunnel.com`
- `https://camera-drowsiness.<tunnel-id>.cfargotunnel.com`

---

### Step 5: Create Config File

```bash
# Create config directory
mkdir -p ~/.cloudflared

# Create config file
nano ~/.cloudflared/config.yml
```

**Paste konfigurasi ini** (ganti `<TUNNEL-ID>` dan URL):

```yaml
tunnel: <TUNNEL-ID>
credentials-file: /home/entung/.cloudflared/<TUNNEL-ID>.json

ingress:
  # Backend API
  - hostname: api-drowsiness.your-domain.com
    service: http://localhost:5001
  
  # Camera Stream
  - hostname: camera-drowsiness.your-domain.com
    service: http://localhost:8080
  
  # Catch-all
  - service: http_status:404
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Step 6: Test Tunnel

```bash
cloudflared tunnel run drowsiness-pi
```

**Expected output:**
```
INF Starting tunnel tunnelID=<TUNNEL-ID>
INF Connection registered connIndex=0
INF Connection registered connIndex=1
INF Connection registered connIndex=2
INF Connection registered connIndex=3
```

**Test dari browser:**
```
https://api-drowsiness.your-domain.com/api/health
https://camera-drowsiness.your-domain.com/health
```

Jika berhasil, Anda akan lihat response dari backend!

**Stop tunnel:** `Ctrl+C`

---

### Step 7: Setup Auto-Start (Systemd)

```bash
# Install as service
sudo cloudflared service install

# Start service
sudo systemctl start cloudflared

# Enable on boot
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

**Expected output:**
```
● cloudflared.service - cloudflared
   Loaded: loaded
   Active: active (running)
```

---

## ✅ Verification

### Test 1: Check Tunnel Status

```bash
cloudflared tunnel info drowsiness-pi
```

### Test 2: Test Endpoints

```bash
# Backend API
curl https://api-drowsiness.your-domain.com/api/health

# Camera Stream
curl https://camera-drowsiness.your-domain.com/health
```

### Test 3: From Browser

Open browser:
```
https://api-drowsiness.your-domain.com/api/health
```

Should see:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "TFLite INT8"
}
```

---

## 🔧 Troubleshooting

### Tunnel Not Starting

**Check logs:**
```bash
sudo journalctl -u cloudflared -f
```

**Common issues:**
- Config file syntax error → Check YAML indentation
- Credentials file not found → Check path in config
- Port already in use → Check if backend running

### DNS Not Resolving

**Check DNS:**
```bash
nslookup api-drowsiness.your-domain.com
```

**If not found:**
- Wait 5-10 minutes for DNS propagation
- Re-run `cloudflared tunnel route dns` command

### Connection Refused

**Check backend:**
```bash
curl http://localhost:5001/api/health
```

If this fails, backend not running. Start it:
```bash
cd ~/deteksikantuk
python backend_server.py
```

---

## 📊 Monitoring

### View Tunnel Logs

```bash
# Real-time logs
sudo journalctl -u cloudflared -f

# Last 100 lines
sudo journalctl -u cloudflared -n 100
```

### Check Tunnel Status

```bash
cloudflared tunnel list
```

### Cloudflare Dashboard

1. Login to Cloudflare Dashboard
2. Go to **Zero Trust** → **Access** → **Tunnels**
3. See your tunnel status, traffic, etc.

---

## 🎯 Next Steps

After Cloudflare Tunnel is running:

1. ✅ Note your tunnel URLs
2. ✅ Update `vercel.json` with your URLs
3. ✅ Deploy to Vercel (see `VERCEL_DEPLOYMENT.md`)
4. ✅ Test end-to-end

---

## 💡 Tips

1. **Use custom domain** for cleaner URLs (optional)
2. **Enable Cloudflare Access** for authentication (optional)
3. **Monitor tunnel logs** regularly
4. **Keep cloudflared updated**: `sudo cloudflared update`

---

Selamat! Raspberry Pi Anda sekarang accessible dari internet dengan HTTPS! 🎉
