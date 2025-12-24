# Hardware Setup Guide - Buzzer & RGB LED

## 🎯 Overview

Panduan lengkap untuk memasang dan mengkonfigurasi buzzer dan RGB LED pada Raspberry Pi untuk sistem deteksi kantuk.

---

## 📦 Komponen yang Dibutuhkan

1. **Buzzer Aktif 5V** - 1 buah
2. **RGB LED Common Cathode** - 1 buah (4 pin: R, G, B, GND)
3. **Resistor 220Ω** - 3 buah (untuk R, G, B)
4. **Breadboard** - 1 buah
5. **Kabel Jumper** - secukupnya

---

## 🔌 Wiring Diagram

### Koneksi GPIO

```
Raspberry Pi GPIO → Komponen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUZZER:
  GPIO17 ────────────→ Buzzer (+)
  GND ───────────────→ Buzzer (-)

RGB LED (Common Cathode):
  GPIO22 ──→ 220Ω ──→ LED Red (R)
  GPIO27 ──→ 220Ω ──→ LED Green (G)
  GPIO24 ──→ 220Ω ──→ LED Blue (B)
  GND ───────────────→ LED Cathode (-)
```

### Diagram Visual

```
┌─────────────────────────────────────┐
│      Raspberry Pi GPIO              │
│                                     │
│  [GPIO17] ─────────────┐            │
│                        │            │
│  [GPIO22] ──┬─ 220Ω ──┼───┐        │
│  [GPIO27] ──┼─ 220Ω ──┼───┼─┐      │
│  [GPIO24] ──┼─ 220Ω ──┼───┼─┼─┐    │
│             │          │   │ │ │    │
│  [GND] ─────┼──────────┼───┼─┼─┼─┐  │
│             │          │   │ │ │ │  │
└─────────────┼──────────┼───┼─┼─┼─┼──┘
              │          │   │ │ │ │
              ▼          ▼   ▼ ▼ ▼ ▼
         ┌────────┐   ┌──────────────┐
         │ BUZZER │   │   RGB LED    │
         │   +  - │   │ R  G  B  -   │
         └────────┘   └──────────────┘
```

---

## ⚙️ GPIO Pin Configuration

| Komponen | Pin GPIO | Pin Fisik | Warna Kabel (Saran) |
|----------|----------|-----------|---------------------|
| Buzzer (+) | GPIO17 | Pin 11 | Merah |
| LED Red | GPIO22 | Pin 15 | Merah |
| LED Green | GPIO27 | Pin 13 | Hijau |
| LED Blue | GPIO24 | Pin 18 | Biru |
| GND | GND | Pin 6, 9, 14, 20 | Hitam |

---

## 🔧 Instalasi Software

### 1. Install Dependencies

```bash
cd ~/deteksikantuk
source venv/bin/activate

# Install RPi.GPIO (biasanya sudah terinstall)
pip install RPi.GPIO
```

### 2. Setup GPIO Permissions

```bash
# Tambahkan user ke group gpio
sudo usermod -a -G gpio $USER

# Logout dan login lagi untuk apply
# Atau reboot
sudo reboot
```

---

## 🧪 Testing Hardware

### Test 1: Hardware Test Script

```bash
cd ~/deteksikantuk
python hardware_alert.py
```

**Expected output:**
```
🔔 HARDWARE ALERT SYSTEM TEST
✅ Hardware alert system initialized
   Buzzer: GPIO17
   RGB LED: R=GPIO22, G=GPIO27, B=GPIO24

🔧 Testing hardware...
Testing GREEN LED...
Testing YELLOW LED...
Testing RED LED...
Testing buzzer...
Turning off...
✅ Hardware test complete!
```

**Verifikasi:**
- ✅ LED hijau menyala (1 detik)
- ✅ LED kuning menyala (1 detik)
- ✅ LED merah menyala (1 detik)
- ✅ Buzzer berbunyi beep-beep (2 detik)
- ✅ Semua mati

### Test 2: Integration Test

```bash
# Terminal 1
python backend_server.py

# Terminal 2
python camera_stream.py

# Buka browser
# http://192.168.0.108:8000/drowsiness_test.html
```

**Test scenario:**
1. **Eyes Open** → LED GREEN, Buzzer OFF
2. **Half Closed** → LED YELLOW, Buzzer OFF
3. **Eyes Closed** → LED RED, Buzzer BEEP

---

## 💡 Alert Logic

### Status Levels

| Status | LED Color | Confidence | Buzzer | Keterangan |
|--------|-----------|------------|--------|------------|
| 🟢 **Alert** | Green | > 0.7 | OFF | Driver terjaga |
| 🟡 **Warning** | Yellow | 0.4 - 0.7 | OFF | Peringatan awal |
| 🔴 **Drowsy** | Red | < 0.4 | ON | Mengantuk - buzzer aktif |

### Buzzer Pattern

- **Pattern**: Beep (0.5s ON, 0.5s OFF)
- **Activation**: Hanya saat status DROWSY
- **Stop**: Langsung saat driver kembali alert

---

## 🔍 Troubleshooting

### LED tidak menyala

**Check 1: Wiring**
```bash
# Test GPIO output
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(22, GPIO.OUT); GPIO.output(22, GPIO.HIGH); import time; time.sleep(2); GPIO.cleanup()"
```

**Check 2: Resistor**
- Pastikan pakai 220Ω (Red-Red-Brown)
- Jangan terlalu besar (LED redup) atau kecil (LED rusak)

**Check 3: LED Polarity**
- Kaki panjang = Anode (R/G/B)
- Kaki pendek = Cathode (GND)

### Buzzer tidak bunyi

**Check 1: Buzzer Type**
- Pastikan pakai **Active Buzzer** (ada oscillator internal)
- Passive buzzer perlu PWM signal

**Check 2: Polarity**
- Buzzer punya polaritas (+/-)
- Biasanya ada tanda + di PCB

**Check 3: Voltage**
- Buzzer 5V bisa langsung ke GPIO (3.3V cukup)
- Kalau terlalu pelan, pakai transistor

### Permission Error

```bash
# Error: "RuntimeError: No access to /dev/mem"
sudo usermod -a -G gpio $USER
sudo reboot
```

### GPIO Already in Use

```bash
# Cleanup GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"
```

---

## 🎨 Customization

### Ubah GPIO Pins

Edit `backend_server.py`:
```python
hardware = HardwareAlert(
    buzzer_pin=17,    # Ganti sesuai kebutuhan
    led_red=22,
    led_green=27,
    led_blue=24
)
```

### Ubah Alert Thresholds

Edit `hardware_alert.py`, function `update_status()`:
```python
if confidence <= 0.3:  # Lebih sensitif (default: 0.4)
    self.led_red()
    self.start_buzzer()
elif confidence <= 0.6:  # Lebih sensitif (default: 0.7)
    self.led_yellow()
```

### Ubah Buzzer Pattern

Edit `hardware_alert.py`, function `_beep_pattern()`:
```python
GPIO.output(self.buzzer_pin, GPIO.HIGH)
time.sleep(0.3)  # Beep lebih cepat (default: 0.5)
GPIO.output(self.buzzer_pin, GPIO.LOW)
time.sleep(0.3)
```

---

## ⚡ Tips & Best Practices

1. **Gunakan Breadboard** untuk prototyping
2. **Test satu-satu** komponen sebelum gabung
3. **Cek polaritas** LED dan buzzer
4. **Jangan lupa resistor** untuk LED (220Ω)
5. **Cleanup GPIO** setelah testing
6. **Backup script** sebelum modifikasi

---

## 📸 Photos (Opsional)

Tambahkan foto setup Anda di sini untuk referensi!

---

## ✅ Checklist

- [ ] Semua komponen tersedia
- [ ] Wiring sesuai diagram
- [ ] GPIO permissions OK
- [ ] Hardware test passed
- [ ] Integration test passed
- [ ] LED warna sesuai status
- [ ] Buzzer bunyi saat drowsy
- [ ] Buzzer stop saat alert

---

Selamat! Hardware alert system siap digunakan! 🎉
