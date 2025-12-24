"""
Flask Backend Server for Drowsiness Detection
==============================================
Optimized TFLite backend for Raspberry Pi
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import atexit

# Try TFLite runtime first (lighter), fallback to TensorFlow
try:
    import tflite_runtime.interpreter as tflite
    USING_TFLITE_RUNTIME = True
except ImportError:
    import tensorflow.lite as tflite
    USING_TFLITE_RUNTIME = False

app = Flask(__name__)

# CORS configuration - allow all origins for local network testing
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
MODEL_PATH = 'best_model.tflite'
IMG_SIZE = (224, 224)

# Load model
print("="*60)
print("🚀 DROWSINESS DETECTION BACKEND")
print("="*60)
print(f"Loading model: {MODEL_PATH}")

try:
    interpreter = tflite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print(f"✅ Model loaded!")
    print(f"   Runtime: {'tflite-runtime' if USING_TFLITE_RUNTIME else 'tensorflow.lite'}")
    print(f"   Input: {input_details[0]['shape']}")
    print(f"   Type: {input_details[0]['dtype']}")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("\n💡 Run convert_model.py first to create best_model.tflite")
    interpreter = None

# Initialize hardware alert system
try:
    from hardware_alert import HardwareAlert
    hardware = HardwareAlert()
    print("✅ Hardware alert system ready")
    HARDWARE_ENABLED = True
except Exception as e:
    print(f"⚠️  Hardware alert disabled: {e}")
    print("   (Running without GPIO - OK for testing)")
    hardware = None
    HARDWARE_ENABLED = False

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Helper functions
def base64_to_image(base64_string):
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def get_eye_regions(frame, face_rect):
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
    if eye_img.size == 0 or eye_img.shape[0] < 10 or eye_img.shape[1] < 10:
        return None
    
    eye_resized = cv2.resize(eye_img, IMG_SIZE)
    eye_rgb = cv2.cvtColor(eye_resized, cv2.COLOR_BGR2RGB)
    
    # Handle INT8 or Float32 input
    if input_details[0]['dtype'] == np.uint8:
        eye_array = np.expand_dims(eye_rgb, axis=0).astype(np.uint8)
    else:
        eye_array = np.expand_dims(eye_rgb / 255.0, axis=0).astype(np.float32)
    
    interpreter.set_tensor(input_details[0]['index'], eye_array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    
    # Handle quantized output
    if output_details[0]['dtype'] == np.uint8:
        scale, zero_point = output_details[0]['quantization']
        output = scale * (output.astype(np.float32) - zero_point)
    
    return float(output[0][0])

# API endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'model_loaded': interpreter is not None,
        'model_type': 'TFLite INT8',
        'runtime': 'tflite-runtime' if USING_TFLITE_RUNTIME else 'tensorflow.lite'
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        frame = base64_to_image(data['image'])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            # No face detected - turn off hardware alerts
            if HARDWARE_ENABLED and hardware:
                hardware.led_off()
                hardware.stop_buzzer()
            
            return jsonify({
                'face_detected': False,
                'confidence': None,
                'is_drowsy': None
            })
        
        face = faces[0]
        left_eye, right_eye = get_eye_regions(frame, face)
        
        predictions = []
        for eye in [left_eye, right_eye]:
            pred = predict_eye_region(eye)
            if pred is not None:
                predictions.append(pred)
        
        if not predictions:
            # Eyes not detected - turn off hardware alerts
            if HARDWARE_ENABLED and hardware:
                hardware.led_off()
                hardware.stop_buzzer()
            
            return jsonify({
                'face_detected': True,
                'confidence': None,
                'is_drowsy': None,
                'error': 'Could not extract eye regions'
            })
        
        avg_confidence = float(np.mean(predictions))
        threshold = float(data.get('threshold', 0.5))
        is_drowsy = avg_confidence < threshold
        
        # Update hardware alert
        if HARDWARE_ENABLED and hardware:
            hardware.update_status(avg_confidence, is_drowsy)
        
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

def cleanup():
    """Cleanup hardware on shutdown"""
    if HARDWARE_ENABLED and hardware:
        print("\n🔧 Cleaning up hardware...")
        hardware.cleanup()

if __name__ == '__main__':
    # Register cleanup handler
    atexit.register(cleanup)
    
    print("\n" + "="*60)
    print("Server: http://0.0.0.0:5001")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  POST /api/predict")
    if HARDWARE_ENABLED:
        print("\n🔔 Hardware Alerts: ENABLED")
        print("   Buzzer: GPIO17")
        print("   RGB LED: R=GPIO22, G=GPIO27, B=GPIO24")
    else:
        print("\n⚠️  Hardware Alerts: DISABLED")
    print("="*60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        cleanup()
