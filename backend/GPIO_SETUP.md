# GPIO Hardware Setup - Drowsiness Detection System

## Komponen Hardware

### 1. Buzzer (Active)
- **GPIO Pin**: GPIO 17 (Physical Pin 11)
- **Fungsi**: Alarm suara saat drowsy ≥ 3 detik
- **Tipe**: Active buzzer (langsung bunyi saat diberi tegangan)

### 2. LED Indicators (3 LED Terpisah)
- **Red LED**: GPIO 22 (Physical Pin 15) - Alarm state
- **Yellow LED**: GPIO 27 (Physical Pin 13) - Warning state  
- **Green LED**: GPIO 24 (Physical Pin 18) - Alert state
- **Fungsi**: Indikator visual status drowsiness

### 3. Resistor
- **Nilai**: 220Ω - 330Ω untuk setiap LED
- **Fungsi**: Membatasi arus LED agar tidak terbakar

---

## Pin Mapping

| Component | GPIO Pin | Physical Pin | Wire Color (Suggested) |
|-----------|----------|--------------|------------------------|
| Buzzer (+) | GPIO 17 | Pin 11 | Yellow |
| Buzzer (-) | GND | Pin 6/9/14/20/25/30/34/39 | Black |
| LED Red (+) | GPIO 22 | Pin 15 | Red |
| LED Yellow (+) | GPIO 27 | Pin 13 | Yellow |
| LED Green (+) | GPIO 24 | Pin 18 | Green |
| All LED (-) | GND | Pin 6/9/14/20/25/30/34/39 | Black |

---

## Wiring Diagram

### ASCII Diagram

```
Raspberry Pi GPIO → Komponen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUZZER:
  GPIO17 ────────────→ Buzzer (+)
  GND ───────────────→ Buzzer (-)

LED INDICATORS (3 LED Terpisah):
  GPIO22 ──→ 220Ω ──→ LED Red (+)    ──┐
  GPIO27 ──→ 220Ω ──→ LED Yellow (+) ──┼──→ GND
  GPIO24 ──→ 220Ω ──→ LED Green (+)  ──┘
```

### Raspberry Pi Pinout (Top View)

```
    3.3V  [ 1] [ 2]  5V
   GPIO2  [ 3] [ 4]  5V
   GPIO3  [ 5] [ 6]  GND  ← All LED & Buzzer Ground
   GPIO4  [ 7] [ 8]  GPIO14
     GND  [ 9] [10]  GPIO15
  GPIO17  [11] [12]  GPIO18  ← BUZZER (+)
  GPIO27  [13] [14]  GND     ← LED Yellow
  GPIO22  [15] [16]  GPIO23  ← LED Red
    3.3V  [17] [18]  GPIO24  ← LED Green
  GPIO10  [19] [20]  GND
   GPIO9  [21] [22]  GPIO25
  GPIO11  [23] [24]  GPIO8
     GND  [25] [26]  GPIO7
   GPIO0  [27] [28]  GPIO1
   GPIO5  [29] [30]  GND
   GPIO6  [31] [32]  GPIO12
  GPIO13  [33] [34]  GND
  GPIO19  [35] [36]  GPIO16
  GPIO26  [37] [38]  GPIO20
     GND  [39] [40]  GPIO21
```

---

## Detailed Wiring Instructions

### Step 1: Buzzer Connection

```
Raspberry Pi          Buzzer
┌─────────────┐      ┌──────┐
│             │      │      │
│  GPIO 17    │─────▶│  +   │
│  (Pin 11)   │      │      │
│             │      │      │
│  GND        │─────▶│  -   │
│  (Pin 6)    │      │      │
└─────────────┘      └──────┘
```

### Step 2: LED Connections

#### Red LED (Alarm State)
```
Raspberry Pi          Red LED
┌─────────────┐      ┌────────┐
│             │      │        │
│  GPIO 22    │──[220Ω]────▶│  +     │
│  (Pin 15)   │      │        │
│             │      │        │
│  GND        │─────────────▶│  -     │
│  (Pin 6)    │      │        │
└─────────────┘      └────────┘
```

#### Yellow LED (Warning State)
```
Raspberry Pi          Yellow LED
┌─────────────┐      ┌────────┐
│             │      │        │
│  GPIO 27    │──[220Ω]────▶│  +     │
│  (Pin 13)   │      │        │
│             │      │        │
│  GND        │─────────────▶│  -     │
│  (Pin 6)    │      │        │
└─────────────┘      └────────┘
```

#### Green LED (Alert State)
```
Raspberry Pi          Green LED
┌─────────────┐      ┌────────┐
│             │      │        │
│  GPIO 24    │──[220Ω]────▶│  +     │
│  (Pin 18)   │      │        │
│             │      │        │
│  GND        │─────────────▶│  -     │
│  (Pin 6)    │      │        │
└─────────────┘      └────────┘
```

---

## Status Indicators

### LED Behavior

| Status | LED Active | Buzzer | Duration | Meaning |
|--------|-----------|--------|----------|---------|
| **No Face** | All OFF | OFF | - | Tidak ada wajah terdeteksi |
| **Alert** | 🟢 Green | OFF | - | Mata terbuka, waspada |
| **Warning** | 🟡 Yellow | OFF | 0-3 detik | Mata tertutup, belum alarm |
| **Alarm** | 🔴 Red | ON | ≥3 detik | Kantuk terdeteksi! |

### Detailed State Machine

```
┌─────────────┐
│  No Face    │ → All LED OFF, Buzzer OFF
└─────────────┘
       ↓
┌─────────────┐
│   Alert     │ → Green LED ON, Buzzer OFF
│ (Eyes Open) │
└─────────────┘
       ↓ (Eyes Close)
┌─────────────┐
│  Warning    │ → Yellow LED ON, Buzzer OFF
│  (0-3 sec)  │    Timer counting...
└─────────────┘
       ↓ (≥3 seconds)
┌─────────────┐
│   ALARM!    │ → Red LED ON, Buzzer ON
│  (≥3 sec)   │    ⚠️ DROWSY DETECTED!
└─────────────┘
       ↓ (Eyes Open)
┌─────────────┐
│   Alert     │ → Green LED ON, Buzzer OFF
│  (Reset)    │    Timer reset
└─────────────┘
```

---

## Code Configuration

### GPIO Pin Definitions (app.py)

```python
class HardwareAlert:
    BUZZER_PIN = 17      # GPIO 17 (Pin 11)
    LED_RED_PIN = 22     # GPIO 22 (Pin 15) - Alarm
    LED_GREEN_PIN = 27   # GPIO 27 (Pin 13) - Alert (was yellow)
    LED_BLUE_PIN = 24    # GPIO 24 (Pin 18) - Warning (was green)
```

**Note:** Dalam kode, kita gunakan:
- `led_green()` untuk Alert state (GPIO 24)
- `led_yellow()` untuk Warning state (GPIO 27 + 22)
- `led_red()` untuk Alarm state (GPIO 22)

---

## Installation Steps

### 1. Prepare Components

**Shopping List:**
- [ ] 1x Active Buzzer (3.3V atau 5V)
- [ ] 1x Red LED (5mm)
- [ ] 1x Yellow LED (5mm)
- [ ] 1x Green LED (5mm)
- [ ] 3x Resistor 220Ω (untuk LEDs)
- [ ] Jumper wires (Male-to-Female)
- [ ] Breadboard (optional)

### 2. Wiring

**Buzzer:**
1. Connect buzzer (+) to GPIO 17 (Pin 11)
2. Connect buzzer (-) to GND (Pin 6)

**LEDs:**
1. Red LED: Anode → 220Ω resistor → GPIO 22 (Pin 15), Cathode → GND
2. Yellow LED: Anode → 220Ω resistor → GPIO 27 (Pin 13), Cathode → GND
3. Green LED: Anode → 220Ω resistor → GPIO 24 (Pin 18), Cathode → GND

**Ground Connection:**
- Use a common ground rail on breadboard
- Connect breadboard GND to Raspberry Pi GND (Pin 6)

### 3. Install GPIO Library

```bash
# Di Raspberry Pi
pip install gpiozero lgpio
```

### 4. Test Hardware

```bash
# Test buzzer
python3 -c "from gpiozero import Buzzer; b = Buzzer(17); b.on(); import time; time.sleep(1); b.off()"

# Test Red LED
python3 -c "from gpiozero import PWMLED; led = PWMLED(22); led.on(); import time; time.sleep(1); led.off()"

# Test Yellow LED
python3 -c "from gpiozero import PWMLED; led = PWMLED(27); led.on(); import time; time.sleep(1); led.off()"

# Test Green LED
python3 -c "from gpiozero import PWMLED; led = PWMLED(24); led.on(); import time; time.sleep(1); led.off()"
```

---

## Troubleshooting

### LED Not Lighting

**Check:**
1. LED polarity (long leg = anode/+, short leg = cathode/-)
2. Resistor value (220-330Ω)
3. GPIO pin number correct
4. Ground connection secure

**Test LED:**
```bash
# Direct test (bypass resistor for testing only!)
python3 -c "from gpiozero import LED; led = LED(22); led.on()"
```

### Buzzer Not Sounding

**Check:**
1. Buzzer type (active vs passive)
2. Polarity (+/-)
3. GPIO 17 connection
4. Ground connection

**Test Buzzer:**
```bash
# Continuous beep
python3 -c "from gpiozero import Buzzer; b = Buzzer(17); b.on(); input('Press Enter to stop'); b.off()"
```

### Permission Denied

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Logout and login again
```

---

## Safety Notes

⚠️ **Important:**
- Always use resistors with LEDs (220-330Ω)
- Don't connect LED directly to GPIO without resistor
- LED forward voltage: Red ~2V, Yellow ~2V, Green ~2.2V
- GPIO max current: 16mA per pin
- Active buzzer has polarity (+/-)
- Don't exceed 3.3V on GPIO pins

---

## Physical Layout Example

```
Breadboard Layout:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Raspberry Pi
    ┌─────────┐
    │         │
    │  GPIO17 │──────→ Buzzer (+)
    │  GPIO22 │──[R]──→ Red LED (+)
    │  GPIO27 │──[R]──→ Yellow LED (+)
    │  GPIO24 │──[R]──→ Green LED (+)
    │  GND    │──────→ Common Ground Rail
    │         │
    └─────────┘
         │
         ↓
    Breadboard
    ┌─────────────────────────┐
    │  [Buzzer]               │
    │  [Red LED]   [220Ω]     │
    │  [Yellow LED] [220Ω]    │
    │  [Green LED]  [220Ω]    │
    │  ═══════════════════    │ ← Ground Rail
    └─────────────────────────┘
```

---

## Verification Checklist

- [ ] All components purchased
- [ ] Buzzer wired to GPIO 17
- [ ] Red LED wired to GPIO 22 with resistor
- [ ] Yellow LED wired to GPIO 27 with resistor
- [ ] Green LED wired to GPIO 24 with resistor
- [ ] All grounds connected
- [ ] Test commands successful
- [ ] Application shows "✅ Hardware initialized"
- [ ] Green LED lights when alert
- [ ] Yellow LED lights during warning (0-3s drowsy)
- [ ] Red LED + Buzzer active during alarm (≥3s drowsy)

---

## References

- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- LED Forward Voltage: Red 1.8-2.2V, Yellow 2.0-2.2V, Green 2.0-3.0V
- Resistor calculation: R = (Vsource - Vled) / Iled = (3.3V - 2V) / 0.015A ≈ 220Ω

---

**Status:** Ready for hardware assembly! 🔧
