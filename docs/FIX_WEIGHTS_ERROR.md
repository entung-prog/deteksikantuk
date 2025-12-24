# Quick Fix: Weights Loading Error

## ❌ Error
```
Error loading weights: Layer 'Conv1' expected 1 variables, but received 0 variables
```

## 🔧 Solution: Use SavedModel Format

### Step 1: Fix Model on Raspberry Pi

```bash
# On Raspberry Pi
cd ~/deteksikantuk
source venv/bin/activate

# Run fix script
python fix_model_formats.py
```

This will create:
- `saved_model/` - SavedModel format (most compatible)
- `best_model_fixed.h5` - Fixed H5 format
- `model_weights_fixed.h5` - Fixed weights

### Step 2: Use SavedModel Backend

```bash
# Run backend with SavedModel
python backend_server_savedmodel.py
```

Expected output:
```
📦 Loading SavedModel...
✅ SavedModel loaded successfully!
   Model path: saved_model
   
🚀 DROWSINESS DETECTION BACKEND SERVER
Server running on: http://0.0.0.0:5001
```

### Step 3: Test

```bash
curl http://localhost:5001/api/health
```

Expected:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_type": "TensorFlow SavedModel"
}
```

---

## 📋 Alternative Solutions

### Option 1: Use Updated backend_server_weights.py

```bash
# Pull latest changes
git pull

# Run updated backend (has fallback methods)
python backend_server_weights.py
```

### Option 2: Use TFLite (RECOMMENDED)

```bash
# Convert to TFLite on laptop first
# Then copy to Raspberry Pi
python backend_server_tflite.py
```

---

## 🎯 Recommended Approach

**For quick fix:** Use SavedModel (Option above)

**For production:** Convert to INT8 TFLite (best performance)

---

## 💡 Why This Error Happened

The `model_weights.weights.h5` file format doesn't match the MobileNetV2 architecture we rebuilt. SavedModel format is more robust and handles version differences better.
