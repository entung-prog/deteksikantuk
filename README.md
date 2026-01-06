# 🚗 Drowsiness Detection System

Sistem deteksi kantuk real-time menggunakan AI pada Raspberry Pi dengan berbagai mode operasi.

## ✨ Fitur Utama

- 🎯 **4 Mode Aplikasi** - Manual, Web Auto, CLI Auto, GUI Auto
- 🤖 **AI Detection** - TensorFlow Lite model untuk deteksi mata tertutup
- 📹 **Camera Preview** - Bounding boxes untuk wajah dan mata
- 💡 **LED Indicators** - Visual feedback (hijau/kuning/merah)
- 🔔 **Buzzer Alert** - Peringatan suara saat kantuk terdeteksi
- 📊 **Statistics** - Tracking deteksi real-time
- 🚀 **Autostart** - Otomatis jalan saat boot

## 📁 Struktur Proyek

```
deteksikantuk/
├── backend/
│   ├── app.py                      # Manual testing (web GUI)
│   ├── app_auto.py                 # Auto-detection (web GUI)
│   ├── app_auto_cli.py             # Auto-detection (CLI only)
│   ├── app_auto_gui.py             # Auto-detection (OpenCV window) ⭐ NEW!
│   ├── best_model_compatible.tflite # Model AI
│   ├── run_app.sh                  # Interactive launcher
│   ├── GUI_AUTO_README.md          # Dokumentasi GUI mode
│   ├── CLI_AUTO_README.md          # Dokumentasi CLI mode
│   ├── VERSIONS_README.md          # Perbandingan semua versi
│   └── requirements.txt
├── autostart/                      # Autostart scripts
├── docs_laporan/                   # Dokumentasi skripsi (tidak di-git)
└── README.md
```

## 🚀 Quick Start

### Pilih Mode Aplikasi

**1. Manual Testing (Web GUI)**
```bash
cd ~/deteksikantuk/backend
python3 app.py
# Buka browser: http://localhost:5000
```

**2. Auto Web (Remote Monitoring)**
```bash
python3 app_auto.py
# Akses dari device lain: http://<raspberry-pi-ip>:5000
```

**3. Auto CLI (Headless)**
```bash
python3 app_auto_cli.py
# Output di terminal, tanpa GUI
```

**4. Auto GUI (Local Monitoring) ⭐ RECOMMENDED**
```bash
python3 app_auto_gui.py
# Preview kamera di window OpenCV
# Controls: ESC=Exit, SPACE=Pause
```

### Atau Gunakan Launcher Interaktif
```bash
cd ~/deteksikantuk/backend
./run_app.sh
# Pilih mode yang diinginkan
```

## 📊 Perbandingan Mode

| Mode | Interface | Auto-Detect | Preview | Remote Access | Display Required |
|------|-----------|-------------|---------|---------------|------------------|
| app.py | Web | ❌ | ✅ Web | ✅ | ❌ |
| app_auto.py | Web | ✅ | ✅ Web | ✅ | ❌ |
| app_auto_cli.py | Terminal | ✅ | ❌ | ❌ | ❌ |
| **app_auto_gui.py** | **OpenCV** | **✅** | **✅ Window** | **❌** | **✅** |

**Lihat detail**: [backend/VERSIONS_README.md](backend/VERSIONS_README.md)

## 🔧 Setup Autostart

### GUI Mode (Dengan Display)
```bash
cd ~/deteksikantuk/backend
./setup_autostart_gui.sh
sudo reboot
```

### Web Mode (Remote Access)
```bash
cd ~/deteksikantuk/autostart
./setup_autostart_auto.sh
sudo reboot
```

**Dokumentasi lengkap**: [AUTOSTART_AUTO.md](AUTOSTART_AUTO.md)

## ⏹️ Menghentikan Aplikasi

**Tekan `Ctrl+C` di terminal**, atau:

```bash
# Kill semua instance
pkill -f "python3 app"

# Matikan hardware (buzzer/LED)
python3 -c "from gpiozero import Buzzer, PWMLED; Buzzer(17).off(); PWMLED(22).off(); PWMLED(27).off(); PWMLED(24).off(); print('Hardware OFF')"
```

## 🔌 Hardware (GPIO)

| Komponen  | Pin GPIO |
|-----------|----------|
| Buzzer    | GPIO 17  |
| LED Merah | GPIO 22  |
| LED Hijau | GPIO 27  |
| LED Biru  | GPIO 24  |

**Setup lengkap**: [backend/GPIO_SETUP.md](backend/GPIO_SETUP.md)

## 📊 Logika Deteksi

| Status | Kondisi | LED | Buzzer | Durasi |
|--------|---------|-----|--------|--------|
| **Alert** | Mata terbuka | 🟢 Hijau | Mati | - |
| **Warning** | Mata tertutup | 🟡 Kuning | Mati | < 3s |
| **Alarm** | Mata tertutup | 🔴 Merah | Nyala | ≥ 3s |
| **No Face** | Wajah tidak terdeteksi | ⚫ Off | Mati | - |

## 📚 Dokumentasi

- **[GUI_AUTO_README.md](backend/GUI_AUTO_README.md)** - GUI mode dengan OpenCV window
- **[CLI_AUTO_README.md](backend/CLI_AUTO_README.md)** - CLI mode headless
- **[VERSIONS_README.md](backend/VERSIONS_README.md)** - Perbandingan semua versi
- **[GPIO_SETUP.md](backend/GPIO_SETUP.md)** - Setup hardware GPIO
- **[TROUBLESHOOTING.md](backend/TROUBLESHOOTING.md)** - Troubleshooting guide
- **[TETHERING_GUIDE.md](TETHERING_GUIDE.md)** - USB tethering untuk remote access

## 🛠️ Troubleshooting

### Kamera tidak terdeteksi
```bash
ls -la /dev/video*
# Coba restart kamera service
```

### Model tidak load
```bash
ls -lh backend/best_model_compatible.tflite
# Pastikan file ada dan readable
```

### GPIO tidak berfungsi
```bash
# Cek apakah gpiozero terinstall
pip3 list | grep gpiozero
```

**Lihat**: [backend/TROUBLESHOOTING.md](backend/TROUBLESHOOTING.md)

## 🎯 Use Cases

- **Testing/Development**: Gunakan `app.py`
- **Remote Monitoring**: Gunakan `app_auto.py`
- **In-Car (dengan display)**: Gunakan `app_auto_gui.py` ⭐
- **In-Car (tanpa display)**: Gunakan `app_auto_cli.py`
- **Production Headless**: Gunakan `app_auto_cli.py`

## 📦 Dependencies

```bash
pip install opencv-python numpy flask
pip install tflite-runtime  # atau tensorflow-lite
pip install gpiozero        # untuk GPIO
```

## 🔗 Repository

GitHub: [https://github.com/entung-prog/deteksikantuk](https://github.com/entung-prog/deteksikantuk)

## 📝 License

Proyek skripsi - Educational purposes
