"""
Flask Backend Server - Using TensorFlow SavedModel
===================================================
Most compatible format, works across different TF versions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import tensorflow as tf

app = Flask(__name__)
CORS(app)

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = 'saved_model'  # SavedModel directory
IMG_SIZE = (224, 224)

# ============================================================
# LOAD SAVEDMODEL
# ============================================================

print("="*60)
print("📦 Loading SavedModel...")

try:
    model = tf.saved_model.load(MODEL_PATH)
    # Get inference function
    infer = model.signatures['serving_default']
    
    print("✅ SavedModel loaded successfully!")
    print(f"   Model path: {MODEL_PATH}")
    print(f"   Available signatures: {list(model.signatures.keys())}")
    
    # Get input/output names
    input_name = list(infer.structured_input_signature[1].keys())[0]
    output_name = list(infer.structured_outputs.keys())[0]
    
    print(f"   Input name: {input_name}")
    print(f"   Output name: {output_name}")
    
except Exception as e:
    print(f"❌ Error loading SavedModel: {e}")
    print("\n💡 Run fix_model_formats.py first to create SavedModel")
    model = None
    infer = None

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
    
    eye_y1 = y + int(h * 0.15)
    eye_y2 = y + int(h * 0.45)
    
    left_x1 = x + int(w * 0.55)
    left_x2 = x + int(w * 0.95)
    
    right_x1 = x + int(w * 0.05)
    right_x2 = x + int(w * 0.45)
    
    left_eye = frame[eye_y1:eye_y2, left_x1:left_x2]
    right_eye = frame[eye_y1:eye_y2, right_x1:right_x2]
    
    return left_eye, right_eye

def predict_eye_region(eye_img):
    """Predict from eye region using SavedModel"""
    if eye_img.size == 0 or eye_img.shape[0] < 10 or eye_img.shape[1] < 10:
        return None
    
    # Preprocess
    eye_resized = cv2.resize(eye_img, IMG_SIZE)
    eye_rgb = cv2.cvtColor(eye_resized, cv2.COLOR_BGR2RGB)
    eye_array = np.expand_dims(eye_rgb / 255.0, axis=0).astype(np.float32)
    
    # Convert to tensor
    input_tensor = tf.constant(eye_array)
    
    # Predict using SavedModel
    prediction = infer(**{input_name: input_tensor})
    output = prediction[output_name].numpy()
    
    return float(output[0][0])

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'model_type': 'TensorFlow SavedModel',
        'model_path': MODEL_PATH
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict drowsiness from image"""
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
        
        # Determine drowsiness
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
    print("🚀 DROWSINESS DETECTION BACKEND SERVER")
    print("="*60)
    print("Server running on: http://0.0.0.0:5001")
    print("API endpoints:")
    print("  - GET  /api/health  - Health check")
    print("  - POST /api/predict - Predict drowsiness")
    print(f"Model: TensorFlow SavedModel ({MODEL_PATH})")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
