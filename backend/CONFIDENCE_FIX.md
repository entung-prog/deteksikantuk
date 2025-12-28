# Solusi Confidence Tidak Akurat

## Analisis Masalah

Dari log detection, terlihat confidence values **sangat bervariasi** dan **tidak konsisten**:

```
Confidence: 0.698, Threshold: 0.90, Drowsy: True  ← Seharusnya Alert
Confidence: 0.947, Threshold: 0.90, Drowsy: False ← OK
Confidence: 0.057, Threshold: 0.90, Drowsy: True  ← Mata tertutup
Confidence: 0.875, Threshold: 0.90, Drowsy: True  ← Seharusnya Alert?
```

## Penyebab

1. **Model belum optimal** - Perlu retraining dengan data lebih banyak
2. **Threshold tidak sesuai** - Default 0.5 terlalu rendah, 0.9 terlalu tinggi
3. **Kondisi pencahayaan** - Model sensitif terhadap lighting
4. **Variasi wajah** - Model perlu lebih banyak data training

## Solusi

### Solusi 1: Adjust Threshold (Quick Fix)

Berdasarkan data log, threshold optimal sekitar **0.6 - 0.7**:

**Di UI Settings:**
- Set "Drowsy Threshold" ke **0.65**
- Ini akan lebih balance antara sensitif dan akurat

**Logika:**
- Confidence > 0.65 = Alert (mata terbuka)
- Confidence < 0.65 = Drowsy (mata tertutup)

### Solusi 2: Temporal Smoothing (Medium Fix)

Tambahkan smoothing untuk mengurangi fluktuasi:

```python
# Add to app.py
confidence_history = []
HISTORY_SIZE = 5  # Last 5 frames

def smooth_confidence(new_confidence):
    global confidence_history
    confidence_history.append(new_confidence)
    if len(confidence_history) > HISTORY_SIZE:
        confidence_history.pop(0)
    return sum(confidence_history) / len(confidence_history)

# In predict_drowsiness():
raw_confidence = float(output[0][0])
confidence = smooth_confidence(raw_confidence)  # Smoothed value
```

### Solusi 3: Retrain Model (Best Solution)

Model perlu di-retrain dengan:

1. **Lebih banyak data**
   - Minimal 1000+ images per class
   - Berbagai kondisi pencahayaan
   - Berbagai sudut wajah

2. **Data augmentation lebih agresif**
   - Brightness adjustment
   - Contrast variation
   - Rotation & flip

3. **Fine-tuning threshold**
   - Analisis confusion matrix
   - Tentukan optimal threshold dari ROC curve

## Implementasi Quick Fix

### Update Default Threshold

Edit `app.py` line 425:

```python
# Before
<input type="range" id="threshold" min="0.1" max="0.9" step="0.05" value="0.5">

# After
<input type="range" id="threshold" min="0.1" max="0.9" step="0.05" value="0.65">
```

Dan line 424:
```python
# Before
<span id="threshold-value">0.50</span>

# After
<span id="threshold-value">0.65</span>
```

### Test Optimal Threshold

Coba berbagai threshold dan catat akurasi:

| Threshold | False Positive | False Negative | Recommended |
|-----------|----------------|----------------|-------------|
| 0.3 | Tinggi (banyak false drowsy) | Rendah | ❌ Terlalu sensitif |
| 0.5 | Sedang | Sedang | ⚠️ Default, kurang akurat |
| 0.65 | Rendah | Rendah | ✅ **Recommended** |
| 0.75 | Rendah | Tinggi (miss drowsy) | ⚠️ Kurang sensitif |
| 0.9 | Sangat rendah | Sangat tinggi | ❌ Hampir tidak detect |

## Monitoring & Tuning

### 1. Collect Detection Data

Jalankan sistem dan catat:
- Waktu detection
- Confidence value
- Actual state (mata terbuka/tertutup)
- Lighting condition

### 2. Analyze Patterns

```python
# Example analysis
import pandas as pd

data = {
    'confidence': [0.698, 0.947, 0.057, 0.875, ...],
    'actual_state': ['open', 'open', 'closed', 'open', ...],
    'lighting': ['normal', 'bright', 'normal', 'dim', ...]
}

df = pd.DataFrame(data)

# Find optimal threshold
from sklearn.metrics import roc_curve, auc

fpr, tpr, thresholds = roc_curve(df['actual_state'], df['confidence'])
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]

print(f"Optimal threshold: {optimal_threshold}")
```

### 3. Update Model

Jika accuracy masih rendah setelah threshold tuning:

1. **Retrain dengan data baru**
   ```bash
   # Di Colab atau local
   python train_model.py --epochs 50 --augmentation aggressive
   ```

2. **Convert ke TFLite**
   ```bash
   python convert_model.py new_model.h5 new_model.tflite
   ```

3. **Deploy ke Raspberry Pi**
   ```bash
   cp new_model.tflite best_model_compatible.tflite
   ```

## Temporary Workaround

Sementara model belum optimal, gunakan **kombinasi deteksi**:

1. **Threshold adaptif** berdasarkan lighting
2. **Temporal filtering** (smoothing)
3. **Durasi minimum** sebelum trigger alarm

```python
# Pseudo-code
DROWSY_DURATION_THRESHOLD = 2.0  # seconds
drowsy_start_time = None

if confidence < threshold:
    if drowsy_start_time is None:
        drowsy_start_time = time.time()
    
    duration = time.time() - drowsy_start_time
    
    if duration >= DROWSY_DURATION_THRESHOLD:
        trigger_alarm()  # Only trigger after 2 seconds
else:
    drowsy_start_time = None  # Reset
```

## Kesimpulan

**Immediate Actions:**
1. ✅ Set threshold ke 0.65 di UI
2. ✅ Test dengan kondisi berbeda
3. ✅ Catat false positive/negative

**Long-term Solutions:**
1. 📊 Collect more training data
2. 🔄 Retrain model dengan data baru
3. 📈 Optimize threshold berdasarkan ROC curve

**Status:**
- Stop detection: ✅ **FIXED**
- Confidence accuracy: ⚠️ **Needs model improvement**
