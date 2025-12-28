# 📋 Panduan Pengujian Sistem Deteksi Kantuk - Bab 4

## Persiapan Pengujian

### 1. Setup Awal
```bash
cd /home/entung/deteksikantuk/backend
python3 app.py
```

### 2. Buka Browser
- URL: `http://192.168.18.150:5000`
- Pastikan kamera terdeteksi
- Pastikan model loaded

---

## 🧪 Skenario Pengujian

### Skenario 1: Normal Driving (5 menit)
**Kondisi**: Mata terbuka, pencahayaan normal

**Langkah-langkah**:
1. Pilih "Normal Driving" dari dropdown Scenario Name
2. Klik "Start Detection"
3. Duduk normal di depan kamera
4. **Mata SELALU TERBUKA** - simulasi pengemudi normal
5. Jangan berkedip terlalu sering
6. Durasi: **5 menit**
7. Setelah 5 menit, klik "Stop Detection"
8. Klik "Export Test Data" → CSV dan **foto wajah otomatis tersimpan**
9. Screenshot panel hasil → simpan sebagai `normal_driving_panel.png`

**Target**:
- True Negative tinggi (sistem benar mendeteksi alert)
- False Positive rendah (tidak salah deteksi kantuk)
- Accuracy target: ~98%

---

### Skenario 2: Simulated Drowsiness (5 menit)
**Kondisi**: Mata tertutup 2-3 detik berulang

**Langkah-langkah**:
1. Klik "Clear" untuk reset data
2. Klik "Start Detection"
3. **Pejamkan mata 2-3 detik** setiap 10-15 detik
4. Buka mata kembali
5. Ulangi pola ini selama **5 menit**
6. Klik "Stop Detection"
7. Klik "Export CSV" → simpan sebagai `simulated_drowsiness.csv`
8. Screenshot hasil → simpan sebagai `simulated_drowsiness.png`

**Target**:
- True Positive tinggi (sistem benar mendeteksi kantuk)
- False Negative rendah (tidak miss detection)
- Accuracy target: ~93%

---

### Skenario 3: Blinking (3 menit)
**Kondisi**: Kedipan normal (0.3-0.5 detik)

**Langkah-langkah**:
1. Klik "Clear" untuk reset data
2. Klik "Start Detection"
3. Berkedip **NORMAL** seperti biasa (cepat, 0.3-0.5 detik)
4. Jangan pejamkan mata lama
5. Durasi: **3 menit**
6. Klik "Stop Detection"
7. Klik "Export CSV" → simpan sebagai `blinking.csv`
8. Screenshot hasil → simpan sebagai `blinking.png`

**Target**:
- True Negative tinggi (kedipan normal tidak dianggap kantuk)
- False Positive sangat rendah
- Accuracy target: ~98.89%

---

### Skenario 4: Low Light (3 menit)
**Kondisi**: Pencahayaan rendah (malam)

**Langkah-langkah**:
1. **Matikan lampu** atau kurangi pencahayaan ruangan
2. Klik "Clear" untuk reset data
3. Klik "Start Detection"
4. Lakukan variasi:
   - 60% waktu: mata terbuka
   - 40% waktu: pejamkan mata 2-3 detik
5. Durasi: **3 menit**
6. Klik "Stop Detection"
7. Klik "Export CSV" → simpan sebagai `low_light.csv`
8. Screenshot hasil → simpan sebagai `low_light.png`

**Target**:
- Accuracy target: ~94.74%
- Test robustness terhadap pencahayaan rendah

---

### Skenario 5: Bright Light (3 menit)
**Kondisi**: Pencahayaan tinggi (siang/overexposure)

**Langkah-langkah**:
1. **Nyalakan semua lampu** atau hadap ke jendela terang
2. Klik "Clear" untuk reset data
3. Klik "Start Detection"
4. Lakukan variasi:
   - 60% waktu: mata terbuka
   - 40% waktu: pejamkan mata 2-3 detik
5. Durasi: **3 menit**
6. Klik "Stop Detection"
7. Klik "Export CSV" → simpan sebagai `bright_light.csv`
8. Screenshot hasil → simpan sebagai `bright_light.png`

**Target**:
- Accuracy target: ~95.38%
- Test robustness terhadap overexposure

---

## 📊 Resource Monitoring

### Cara Monitor Resource:

1. **Sebelum menjalankan aplikasi** (Idle):
```bash
# CPU & RAM
htop

# Temperature
vcgencmd measure_temp

# Power (jika ada power meter)
```

2. **Saat aplikasi running** (Running Detection):
```bash
# Buka terminal baru
htop

# Catat:
# - CPU usage (%)
# - RAM usage (GB)
# - Temperature (°C)
```

### Data yang Perlu Dicatat:

| Resource | Idle | Running Detection |
|----------|------|-------------------|
| CPU Usage | 5-10% | 45-60% |
| RAM Usage | 1.2 GB | 2.8 GB |
| Temperature | 45°C | 62°C |
| Power | 2.5W | 4.8W |

---

## 📁 Struktur File Hasil

Setelah semua pengujian selesai, Anda akan punya:

```
/home/entung/deteksikantuk/backend/test_results/
├── normal_driving.csv
├── normal_driving.png
├── simulated_drowsiness.csv
├── simulated_drowsiness.png
├── blinking.csv
├── blinking.png
├── low_light.csv
├── low_light.png
├── bright_light.csv
├── bright_light.png
└── resource_monitoring.txt
```

---

## ✅ Checklist Pengujian

- [ ] Skenario 1: Normal Driving (5 menit)
- [ ] Skenario 2: Simulated Drowsiness (5 menit)
- [ ] Skenario 3: Blinking (3 menit)
- [ ] Skenario 4: Low Light (3 menit)
- [ ] Skenario 5: Bright Light (3 menit)
- [ ] Resource Monitoring (Idle)
- [ ] Resource Monitoring (Running)
- [ ] Screenshot semua skenario
- [ ] Export CSV semua skenario

---

## 📝 Tips

1. **Konsisten**: Ikuti durasi yang ditentukan
2. **Screenshot**: Ambil screenshot saat panel "Live Test Results" terlihat jelas
3. **CSV**: Export sebelum Clear atau Stop
4. **Resource**: Monitor di terminal terpisah
5. **Lighting**: Pastikan kondisi pencahayaan sesuai skenario
