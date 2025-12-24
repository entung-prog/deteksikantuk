# Vercel Deployment Guide

## 🎯 Overview

Panduan deploy frontend drowsiness detection ke Vercel (gratis) dengan backend di Raspberry Pi via Cloudflare Tunnel.

---

## 📋 Prerequisites

- ✅ Cloudflare Tunnel sudah setup (lihat `CLOUDFLARE_TUNNEL.md`)
- ✅ Punya akun GitHub
- ✅ Repository sudah di GitHub
- ✅ Akun Vercel (gratis)

---

## 🚀 Vercel Deployment

### Step 1: Buat Akun Vercel

1. Buka https://vercel.com
2. Klik **Sign Up**
3. Pilih **Continue with GitHub**
4. Authorize Vercel

---

### Step 2: Import Project

1. Di Vercel Dashboard, klik **Add New** → **Project**
2. Pilih repository: `entung-/deteksikantuk`
3. Klik **Import**

---

### Step 3: Configure Project

**Framework Preset:** None (atau pilih Other)

**Root Directory:** `webtest` (atau `.` jika repo root)

**Build Command:** Leave empty

**Output Directory:** `.`

**Install Command:** Leave empty

---

### Step 4: Environment Variables

Klik **Environment Variables**, tambahkan:

| Name | Value | Example |
|------|-------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Your Cloudflare Tunnel URL | `https://api-drowsiness.abc123.cfargotunnel.com` |
| `NEXT_PUBLIC_CAMERA_URL` | Your Camera Tunnel URL | `https://camera-drowsiness.abc123.cfargotunnel.com` |

**PENTING:** Ganti dengan URL tunnel Anda yang sebenarnya!

---

### Step 5: Deploy

1. Klik **Deploy**
2. Tunggu ~1-2 menit
3. Selesai! 🎉

**Your site is live at:** `https://your-project.vercel.app`

---

## 🔧 Update vercel.json

Sebelum deploy, update `vercel.json` dengan URL tunnel Anda:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api-drowsiness.YOUR-TUNNEL-URL.com/api/:path*"
    }
  ],
  "env": {
    "NEXT_PUBLIC_BACKEND_URL": "https://api-drowsiness.YOUR-TUNNEL-URL.com",
    "NEXT_PUBLIC_CAMERA_URL": "https://camera-drowsiness.YOUR-TUNNEL-URL.com"
  }
}
```

**Commit dan push:**
```bash
git add vercel.json
git commit -m "Update Cloudflare Tunnel URLs"
git push
```

Vercel akan auto-deploy!

---

## ✅ Verification

### Test 1: Open Vercel URL

```
https://your-project.vercel.app/drowsiness_test.html
```

**Expected:**
- ✅ Page loads
- ✅ Model Status: ✅ Ready

### Test 2: Test Backend Connection

Open browser console (F12), check Network tab:
- ✅ API calls to Cloudflare Tunnel URL
- ✅ No CORS errors
- ✅ Backend responds

### Test 3: Test Camera Selection

**Option 1: Laptop Webcam**
1. Select "Webcam Laptop"
2. Grant camera permission
3. Click "Start Visualization"
4. ✅ Detection works

**Option 2: Raspberry Pi Camera**
1. Select "Raspberry Pi Camera"
2. Click "Start Visualization"
3. ✅ Camera stream shows
4. ✅ Detection works

### Test 4: Test Hardware Alerts

1. Use Raspberry Pi Camera
2. Close eyes
3. ✅ LED turns red (on Raspberry Pi)
4. ✅ Buzzer beeps (on Raspberry Pi)

---

## 🔄 Auto-Deploy

Vercel akan otomatis deploy setiap kali Anda push ke GitHub!

```bash
# Make changes
git add .
git commit -m "Update frontend"
git push

# Vercel auto-deploys!
```

**Check deployment:**
- Vercel Dashboard → Your Project → Deployments

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain

1. Di Vercel Dashboard → Your Project → **Settings** → **Domains**
2. Klik **Add**
3. Enter your domain: `drowsiness.your-domain.com`
4. Follow DNS instructions

**DNS Setup:**
- Add CNAME record: `drowsiness` → `cname.vercel-dns.com`

---

## 🔧 Troubleshooting

### CORS Error

**Problem:** `Access-Control-Allow-Origin` error

**Solution:**
1. Check `backend_server.py` CORS config
2. Add Vercel domain to allowed origins:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-project.vercel.app",
            "https://drowsiness.your-domain.com"
        ]
    }
})
```

### Backend Not Responding

**Check:**
1. Cloudflare Tunnel running? `sudo systemctl status cloudflared`
2. Backend running? `curl http://localhost:5001/api/health`
3. Tunnel URL correct in `vercel.json`?

### Camera Not Working

**Laptop Webcam:**
- Grant camera permission in browser
- Check browser console for errors

**Raspberry Pi Camera:**
- Check camera stream: `curl http://localhost:8080/health`
- Check Cloudflare Tunnel for camera URL

---

## 📊 Monitoring

### Vercel Analytics

1. Vercel Dashboard → Your Project → **Analytics**
2. See:
   - Page views
   - Performance
   - Errors

### Deployment Logs

1. Vercel Dashboard → Your Project → **Deployments**
2. Click on deployment
3. View **Build Logs** and **Function Logs**

---

## 💡 Tips

1. **Use Preview Deployments**
   - Every branch gets a preview URL
   - Test before merging to main

2. **Environment Variables per Environment**
   - Production: `https://api.your-domain.com`
   - Preview: `https://api-dev.your-domain.com`

3. **Enable Vercel Speed Insights**
   - Free performance monitoring
   - Settings → Speed Insights → Enable

---

## 🎯 Final Architecture

```
User Browser
    ↓
Vercel (Frontend)
    ↓
Cloudflare Tunnel
    ↓
Raspberry Pi (Backend + Camera + Hardware)
```

**Benefits:**
- ✅ Accessible from anywhere
- ✅ HTTPS automatic
- ✅ Auto-deploy on push
- ✅ $0/month cost
- ✅ Hardware alerts still work

---

Selamat! Sistem Anda sekarang production-ready! 🚀
