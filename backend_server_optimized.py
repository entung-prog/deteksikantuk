"""
Flask Backend Server for Drowsiness Detection - Optimized for Raspberry Pi
===========================================================================
Memory-optimized version with TensorFlow settings for resource-constrained devices
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import os
import sys

# Optimize TensorFlow for Raspberry Pi
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce logging
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'  # Allow memory growth

import tensorflow as tf

# Limit TensorFlow memory usage
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

from tensorflow import keras

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# ============================================================
# CONFIGURATION
# ============================================================

WEIGHTS_PATH = 'best_model.h5'  # Model in same directory
IMG_SIZE = (224, 224)

# ============================================================
# BUILD & LOAD MODEL
# ============================================================

print("="*60)
print("🔄 Loading model (this may take 2-5 minutes on Raspberry Pi)...")
print("="*60)

try:
    # Load model with memory optimization
    print("📦 Loading H5 model...")
    model = keras.models.load_model(WEIGHTS_PATH, compile=False)
    
    # Compile with lower precision for faster inference
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Model loaded successfully!")
    print(f"   Input shape: {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Check if best_model.h5 exists")
    print("   2. Increase swap memory to 2GB")
    print("   3. Close other applications")
    print("   4. Wait 2-5 minutes for loading")
    model = None

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def base64_to_image(base64_string):
    """Convert base64 string to OpenCV image"""
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def get_eye_regions(frame, face_rect):
    """Extract left and right eye regions from face"""
    x, y, w, h = face_rect
    
    # Eye region is typically in upper 40% of face
    eye_y1 = y + int(h * 0.15)
    eye_y2 = y + int(h * 0.45)
    
    # Left eye (right side of image due to mirror)
    left_x1 = x + int(w * 0.55)
    left_x2 = x + int(w * 0.95)
    
    # Right eye (left side of image)
    right_x1 = x + int(w * 0.05)
    right_x2 = x + int(w * 0.45)
    
    left_eye = frame[eye_y1:eye_y2, left_x1:left_x2]
    right_eye = frame[eye_y1:eye_y2, right_x1:right_x2]
    
    return left_eye, right_eye

def predict_eye_region(eye_img):
    """Predict from eye region"""
    if eye_img.size == 0 or eye_img.shape[0] < 10 or eye_img.shape[1] < 10:
        return None
    
    eye_resized = cv2.resize(eye_img, IMG_SIZE)
    eye_rgb = cv2.cvtColor(eye_resized, cv2.COLOR_BGR2RGB)
    eye_array = np.expand_dims(eye_rgb / 255.0, axis=0).astype(np.float32)
    
    # Use predict with batch size 1 for memory efficiency
    prediction = model.predict(eye_array, verbose=0, batch_size=1)
    return float(prediction[0][0])

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'model_type': 'TensorFlow/Keras (Optimized)'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict drowsiness from image
    Expects JSON: { "image": "base64_encoded_image" }
    Returns: { "confidence": float, "is_drowsy": bool, "face_detected": bool }
    """
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Convert base64 to image
        frame = base64_to_image(data['image'])
        
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return jsonify({
                'face_detected': False,
                'confidence': None,
                'is_drowsy': None
            })
        
        # Get first face
        face = faces[0]
        
        # Extract eye regions
        left_eye, right_eye = get_eye_regions(frame, face)
        
        # Predict on both eyes
        predictions = []
        left_pred = predict_eye_region(left_eye)
        if left_pred is not None:
            predictions.append(left_pred)
        
        right_pred = predict_eye_region(right_eye)
        if right_pred is not None:
            predictions.append(right_pred)
        
        if not predictions:
            return jsonify({
                'face_detected': True,
                'confidence': None,
                'is_drowsy': None,
                'error': 'Could not extract eye regions'
            })
        
        # Average prediction
        avg_confidence = float(np.mean(predictions))
        
        # Determine drowsiness (threshold from request or default 0.5)
        threshold = float(data.get('threshold', 0.5))
        is_drowsy = avg_confidence < threshold
        
        return jsonify({
            'face_detected': True,
            'confidence': avg_confidence,
            'is_drowsy': is_drowsy,
            'face_box': {
                'x': int(face[0]),
                'y': int(face[1]),
                'width': int(face[2]),
                'height': int(face[3])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DROWSINESS DETECTION BACKEND SERVER (Optimized)")
    print("="*60)
    print("Server running on: http://0.0.0.0:5001")
    print("API endpoints:")
    print("  - GET  /api/health  - Health check")
    print("  - POST /api/predict - Predict drowsiness")
    print("Optimized for: Raspberry Pi")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=False)
