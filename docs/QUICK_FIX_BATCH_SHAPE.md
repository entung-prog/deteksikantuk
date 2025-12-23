# ⚡ Quick Fix - batch_shape Error

## ❌ Error
```
Unrecognized keyword arguments: ['batch_shape']
```

## ✅ Solusi Tercepat

### **Opsi 1: Load dengan compile=False**

**Di Raspberry Pi, edit `backend_server.py` line 42:**

```python
# Dari:
model = keras.models.load_model(WEIGHTS_PATH)

# Ke:
model = keras.models.load_model(WEIGHTS_PATH, compile=False)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
```

**Jalankan:**
```bash
python backend_server.py
```

---

### **Opsi 2: Gunakan Backend dengan Fix**

Saya sudah buat `backend_server_compat.py` dengan fix ini.

```bash
python backend_server_compat.py
```

---

### **Opsi 3: Update TensorFlow di Raspi**

```bash
pip install --upgrade tensorflow==2.15.0
```

---

**Coba Opsi 1 dulu (paling cepat)!** 🚀
