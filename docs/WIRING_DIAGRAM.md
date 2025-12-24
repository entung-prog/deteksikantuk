# Wiring Diagram - Buzzer & RGB LED

## 📍 Raspberry Pi GPIO Pinout (40 Pin)

```
┌─────────────────────────────────────────┐
│  Raspberry Pi GPIO Header (Top View)    │
├─────────────────────────────────────────┤
│                                         │
│  3V3    [ 1] [ 2]  5V                   │
│  GPIO2  [ 3] [ 4]  5V                   │
│  GPIO3  [ 5] [ 6]  GND                  │
│  GPIO4  [ 7] [ 8]  GPIO14               │
│  GND    [ 9] [10]  GPIO15  ◄─── GND Buzzer
│  GPIO17 [11] [12]  GPIO18               │
│  GPIO27 [13] [14]  GND     ◄─── GND LED │
│  GPIO22 [15] [16]  GPIO23               │
│  3V3    [17] [18]  GPIO24               │
│  GPIO10 [19] [20]  GND                  │
│  ...                                    │
└─────────────────────────────────────────┘

PIN YANG DIPAKAI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pin 11 (GPIO17) → Buzzer (+)
Pin 9  (GND)    → Buzzer (-) 
Pin 15 (GPIO22) → LED Red
Pin 13 (GPIO27) → LED Yellow
Pin 18 (GPIO24) → LED Green
Pin 14 (GND)    → LED Cathode (-)
```

---

## 🔌 Koneksi Lengkap dengan Breadboard

```
RASPBERRY PI                    BREADBOARD                    KOMPONEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pin 11 (GPIO17) ──────────────→ Buzzer (+)
        [Merah]                
                               
Pin 9  (GND) ─────────────────→ Buzzer (-)
        [Hitam]                

Pin 15 (GPIO22) ──────────────→ [220Ω] ──→ LED Red (R)
        [Merah]                

Pin 13 (GPIO27) ──────────────→ [220Ω] ──→ LED Yellow (Y)
        [Kuning]                

Pin 18 (GPIO24) ──────────────→ [220Ω] ──→ LED Green (G)
        [Hijau]                

Pin 14 (GND) ─────────────────→ LED Cathode (-)
        [Hitam]
```

---

## 🎨 Detail Komponen

### 1. RYG LED (Common Cathode) - Traffic Light Style 🚦

```
     ┌─────────┐
     │ RYG LED │
     │  ┌───┐  │
     │  │ ● │  │  ← LED di dalam
     │  └───┘  │
     └────┬────┘
          │
    ┌─────┴─────┬─────┬─────┐
    │     │     │     │     │
    R     Y     G     -     
    │     │     │     │
  (Merah)(Kuning)(Hijau)(GND)
    
Kaki LED:
- Kaki 1 (panjang)   = Red (R)
- Kaki 2 (panjang)   = Yellow (Y)  
- Kaki 3 (panjang)   = Green (G)
- Kaki 4 (PENDEK)    = Cathode (-) ke GND
```

### 2. Buzzer Aktif

```
     ┌─────────┐
     │ BUZZER  │
     │  ┌───┐  │
     │  │ ≈ │  │  ← Speaker
     │  └───┘  │
     └────┬────┘
          │
       ┌──┴──┐
       │  │  │
       +  -  
       │  │
    (Positif)(Negatif)
    
Tanda di PCB:
- Ada tanda + di sisi positif
- Atau kabel merah = +, hitam = -
```

### 3. Resistor 220Ω

```
    ┌─────────────┐
────┤ 220Ω       ├────
    └─────────────┘
    
Warna pita:
[Merah][Merah][Coklat][Emas]
  2      2      x10    ±5%
= 22 x 10 = 220Ω
```

---

## 📐 Layout Breadboard (Top View)

```
BREADBOARD LAYOUT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Power Rails:
  (+) ═══════════════════════════════ (tidak dipakai)
  (-) ═══════════════════════════════ GND Rail ← Pin 6 masuk sini
       │  │  │  │
       │  │  │  └──→ LED Cathode
       │  │  └─────→ Buzzer (-)
       │  └────────→ (cadangan)
       └───────────→ (cadangan)

Main Area:
  Row 1:  [GPIO17]───────────────────→ Buzzer (+)
  
  Row 5:  [GPIO22]──[220Ω]──[J3]─────→ LED Red
  
  Row 10: [GPIO27]──[220Ω]──[J5]─────→ LED Green
  
  Row 15: [GPIO24]──[220Ω]──[J7]─────→ LED Blue
```

---

## 🔧 Langkah Pemasangan

### Step 1: Siapkan Breadboard
1. Colok kabel hitam dari **Pin 6 (GND)** ke **GND Rail** breadboard

### Step 2: Pasang Buzzer
1. Colok **Buzzer (+)** ke breadboard
2. Colok kabel merah dari **Pin 11 (GPIO17)** ke **Buzzer (+)**
3. Colok **Buzzer (-)** ke **GND Rail**

### Step 3: Pasang Resistor
1. Pasang 3 resistor 220Ω di breadboard
2. Satu ujung resistor ke hole kosong
3. Ujung lain akan ke LED

### Step 4: Pasang RGB LED
1. Identifikasi kaki LED (kaki pendek = cathode)
2. Colok **LED Red** ke resistor 1
3. Colok **LED Green** ke resistor 2
4. Colok **LED Blue** ke resistor 3
5. Colok **LED Cathode (-)** ke **GND Rail**

### Step 5: Hubungkan GPIO
1. **Pin 15 (GPIO22)** → ujung resistor 1 (untuk Red)
2. **Pin 13 (GPIO27)** → ujung resistor 2 (untuk Green)
3. **Pin 18 (GPIO24)** → ujung resistor 3 (untuk Blue)

---

## ✅ Checklist Pemasangan

- [ ] Kabel GND dari Pi ke GND Rail breadboard
- [ ] Buzzer (+) terhubung ke GPIO17
- [ ] Buzzer (-) terhubung ke GND Rail
- [ ] 3 resistor 220Ω terpasang
- [ ] LED Red terhubung ke GPIO22 via resistor
- [ ] LED Green terhubung ke GPIO27 via resistor
- [ ] LED Blue terhubung ke GPIO24 via resistor
- [ ] LED Cathode (-) terhubung ke GND Rail
- [ ] Semua koneksi kencang dan tidak goyang

---

## 🎯 Tips Penting

1. **Matikan Raspberry Pi** saat memasang komponen
2. **Cek polaritas** LED dan buzzer sebelum colok
3. **Jangan lupa resistor** untuk LED (bisa terbakar!)
4. **Test satu-satu** komponen dengan script test
5. **Gunakan warna kabel** yang sesuai untuk memudahkan

---

Selamat merakit! 🔧
