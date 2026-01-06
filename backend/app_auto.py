"""
Drowsiness Detection - Auto-Detection Version
Automatically detects drowsiness without requiring button presses
Features: Continuous detection, LED visual feedback, automatic warnings
"""

import sys
# Ensure psutil can be imported
if '/usr/lib/python3/dist-packages' not in sys.path:
    sys.path.insert(0, '/usr/lib/python3/dist-packages')

from flask import Flask, Response, render_template_string, request, jsonify
import cv2
import threading
import numpy as np
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================
# GLOBAL VARIABLES
# ============================================================
camera = None
output_frame = None
lock = threading.Lock()
camera_type = None
interpreter = None
input_details = None
output_details = None
face_cascade = None
eye_cascade = None
inference_lock = threading.Lock()
stop_capture_thread = False
stop_detection_thread = False

# Drowsy duration tracking
drowsy_start_time = None
drowsy_duration_threshold = 3.0  # seconds

# Current detection state (for UI display)
current_state = {
    "status": "NO FACE",
    "is_drowsy": False,
    "confidence": None,
    "drowsy_duration": 0,
    "alarm_active": False,
    "face_detected": False
}
state_lock = threading.Lock()

# GPIO Hardware
hardware = None
GPIO_AVAILABLE = False

# Statistics tracking
stats = {
    "total_detections": 0,
    "drowsy_count": 0,
    "alert_count": 0,
    "start_time": None
}

# Try to import GPIO library
try:
    from gpiozero import Buzzer, PWMLED
    GPIO_AVAILABLE = True
    logger.info("GPIO library (gpiozero) available")
except ImportError:
    logger.warning("GPIO library not available - running without hardware alerts")

# ============================================================
# HTML TEMPLATE - AUTO-DETECTION VERSION
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚗 Auto Drowsiness Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        header h1 {
            font-size: 2.8rem;
            background: linear-gradient(90deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .auto-badge {
            display: inline-block;
            background: linear-gradient(135deg, #10b981, #059669);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            animation: pulse-glow 2s infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
            50% { box-shadow: 0 4px 25px rgba(16, 185, 129, 0.7); }
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 25px;
        }
        
        @media (max-width: 1000px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        
        .video-section {
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            padding: 25px;
            border: 2px solid rgba(0, 255, 136, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .video-container {
            position: relative;
            width: 100%;
            aspect-ratio: 4/3;
            background: #000;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }
        
        .video-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .status-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            z-index: 10;
        }
        
        .status-badge {
            padding: 15px 30px;
            border-radius: 40px;
            font-weight: bold;
            font-size: 1.4rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            backdrop-filter: blur(10px);
        }
        
        .status-alert {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9));
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.6);
        }
        
        .status-drowsy {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.95), rgba(220, 38, 38, 0.95));
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.6);
            animation: pulse-danger 1s infinite;
        }
        
        .status-noface {
            background: linear-gradient(135deg, rgba(107, 114, 128, 0.9), rgba(75, 85, 99, 0.9));
        }
        
        @keyframes pulse-danger {
            0%, 100% { transform: scale(1); box-shadow: 0 4px 20px rgba(239, 68, 68, 0.6); }
            50% { transform: scale(1.05); box-shadow: 0 6px 30px rgba(239, 68, 68, 0.9); }
        }
        
        .confidence-badge {
            background: rgba(0,0,0,0.8);
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 1rem;
            backdrop-filter: blur(10px);
        }
        
        .duration-display {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            padding: 12px 20px;
            border-radius: 20px;
            font-size: 1.1rem;
            font-weight: bold;
            backdrop-filter: blur(10px);
        }
        
        .duration-normal { color: #10b981; }
        .duration-warning { color: #f59e0b; }
        .duration-danger { 
            color: #ef4444; 
            animation: blink 0.5s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .side-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .panel-card {
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(0, 255, 136, 0.15);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }
        
        .panel-card h3 {
            font-size: 1.1rem;
            color: #00ff88;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        
        .stat-item {
            background: rgba(0,0,0,0.3);
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stat-label {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 5px;
        }
        
        .led-indicator {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
        }
        
        .led {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            position: relative;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }
        
        .led-green {
            background: radial-gradient(circle, #10b981, #059669);
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.8);
        }
        
        .led-yellow {
            background: radial-gradient(circle, #f59e0b, #d97706);
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.8);
        }
        
        .led-red {
            background: radial-gradient(circle, #ef4444, #dc2626);
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.8);
            animation: pulse-led 0.5s infinite;
        }
        
        .led-off {
            background: #333;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }
        
        @keyframes pulse-led {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .led-label {
            text-align: center;
            margin-top: 8px;
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .alarm-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(239, 68, 68, 0.4);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: flash 0.5s infinite;
            backdrop-filter: blur(5px);
        }
        
        .alarm-overlay.hidden { display: none; }
        
        .alarm-text {
            font-size: 5rem;
            font-weight: bold;
            text-shadow: 0 0 40px rgba(255,255,255,0.9);
            animation: shake 0.5s infinite;
        }
        
        @keyframes flash {
            0%, 100% { background: rgba(239, 68, 68, 0.3); }
            50% { background: rgba(239, 68, 68, 0.6); }
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        .info-text {
            text-align: center;
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 15px;
            padding: 12px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚗 Auto Drowsiness Detection</h1>
            <div class="auto-badge">● LIVE - Auto Detection Active</div>
        </header>
        
        <div class="main-grid">
            <div class="video-section">
                <div class="video-container">
                    <img id="video-stream" src="/video_feed" alt="Camera Stream">
                    
                    <div class="status-overlay">
                        <div id="status-badge" class="status-badge status-noface">NO FACE</div>
                        <div id="confidence-badge" class="confidence-badge">Confidence: --</div>
                    </div>
                    
                    <div id="duration-display" class="duration-display duration-normal">
                        Duration: <span id="duration-value">0.0s</span>
                    </div>
                </div>
                
                <div class="info-text">
                    ✨ Detection runs automatically - no button press needed<br>
                    🚨 Alarm triggers after <strong id="threshold-display">3.0s</strong> of continuous drowsiness
                </div>
            </div>
            
            <div class="side-panel">
                <div class="panel-card">
                    <h3>💡 LED Status Indicators</h3>
                    <div class="led-indicator">
                        <div>
                            <div id="led-green" class="led led-off"></div>
                            <div class="led-label">Alert</div>
                        </div>
                        <div>
                            <div id="led-yellow" class="led led-off"></div>
                            <div class="led-label">Warning</div>
                        </div>
                        <div>
                            <div id="led-red" class="led led-off"></div>
                            <div class="led-label">Alarm</div>
                        </div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <h3>📊 Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div id="total-detections" class="stat-value">0</div>
                            <div class="stat-label">Total</div>
                        </div>
                        <div class="stat-item">
                            <div id="drowsy-count" class="stat-value">0</div>
                            <div class="stat-label">Drowsy</div>
                        </div>
                        <div class="stat-item">
                            <div id="alert-count" class="stat-value">0</div>
                            <div class="stat-label">Alert</div>
                        </div>
                        <div class="stat-item">
                            <div id="uptime" class="stat-value">0s</div>
                            <div class="stat-label">Uptime</div>
                        </div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <h3>⚙️ System Info</h3>
                    <div style="font-size:0.85rem;line-height:1.8">
                        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.1)">
                            <span style="color:#94a3b8">Camera:</span>
                            <span style="color:#00d4ff;font-weight:bold" id="camera-type">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.1)">
                            <span style="color:#94a3b8">Model:</span>
                            <span style="color:#00d4ff;font-weight:bold" id="model-status">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.1)">
                            <span style="color:#94a3b8">Hardware:</span>
                            <span style="color:#00d4ff;font-weight:bold" id="hardware-status">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;padding:8px 0">
                            <span style="color:#94a3b8">FPS:</span>
                            <span style="color:#00d4ff;font-weight:bold" id="fps-display">--</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="alarm-overlay" class="alarm-overlay hidden">
        <div class="alarm-text">⚠️ WAKE UP! ⚠️</div>
    </div>
    
    <script>
        let startTime = Date.now();
        let fpsCounter = 0;
        let lastFpsUpdate = Date.now();
        
        // Auto-start detection on page load
        function autoDetect() {
            fetch('/get_status')
                .then(r => r.json())
                .then(data => {
                    updateUI(data);
                })
                .catch(err => console.error('Detection error:', err));
        }
        
        function updateUI(data) {
            // Update status badge
            const statusBadge = document.getElementById('status-badge');
            const confidenceBadge = document.getElementById('confidence-badge');
            const durationDisplay = document.getElementById('duration-display');
            const durationValue = document.getElementById('duration-value');
            const alarmOverlay = document.getElementById('alarm-overlay');
            
            if (!data.face_detected) {
                statusBadge.textContent = 'NO FACE';
                statusBadge.className = 'status-badge status-noface';
                confidenceBadge.textContent = 'Confidence: --';
                durationValue.textContent = '0.0s';
                durationDisplay.className = 'duration-display duration-normal';
                updateLEDs('off');
                alarmOverlay.classList.add('hidden');
            } else if (data.is_drowsy) {
                statusBadge.textContent = 'DROWSY';
                statusBadge.className = 'status-badge status-drowsy';
                confidenceBadge.textContent = 'Confidence: ' + (data.confidence * 100).toFixed(1) + '%';
                durationValue.textContent = data.drowsy_duration.toFixed(1) + 's';
                
                // Update duration display color based on severity
                if (data.drowsy_duration >= data.alarm_threshold) {
                    durationDisplay.className = 'duration-display duration-danger';
                    updateLEDs('red');
                    alarmOverlay.classList.remove('hidden');
                } else if (data.drowsy_duration >= data.alarm_threshold * 0.5) {
                    durationDisplay.className = 'duration-display duration-warning';
                    updateLEDs('yellow');
                    alarmOverlay.classList.add('hidden');
                } else {
                    durationDisplay.className = 'duration-display duration-warning';
                    updateLEDs('yellow');
                    alarmOverlay.classList.add('hidden');
                }
            } else {
                statusBadge.textContent = 'ALERT';
                statusBadge.className = 'status-badge status-alert';
                confidenceBadge.textContent = 'Confidence: ' + (data.confidence * 100).toFixed(1) + '%';
                durationValue.textContent = '0.0s';
                durationDisplay.className = 'duration-display duration-normal';
                updateLEDs('green');
                alarmOverlay.classList.add('hidden');
            }
            
            // Update statistics
            document.getElementById('total-detections').textContent = data.stats.total;
            document.getElementById('drowsy-count').textContent = data.stats.drowsy;
            document.getElementById('alert-count').textContent = data.stats.alert;
            
            // Update uptime
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('uptime').textContent = uptime + 's';
            
            // Update FPS
            fpsCounter++;
            const now = Date.now();
            if (now - lastFpsUpdate >= 1000) {
                document.getElementById('fps-display').textContent = fpsCounter + ' FPS';
                fpsCounter = 0;
                lastFpsUpdate = now;
            }
        }
        
        function updateLEDs(state) {
            const greenLED = document.getElementById('led-green');
            const yellowLED = document.getElementById('led-yellow');
            const redLED = document.getElementById('led-red');
            
            // Reset all
            greenLED.className = 'led led-off';
            yellowLED.className = 'led led-off';
            redLED.className = 'led led-off';
            
            // Set active LED
            if (state === 'green') {
                greenLED.className = 'led led-green';
            } else if (state === 'yellow') {
                yellowLED.className = 'led led-yellow';
            } else if (state === 'red') {
                redLED.className = 'led led-red';
            }
        }
        
        // Load system info
        fetch('/health')
            .then(r => r.json())
            .then(data => {
                document.getElementById('camera-type').textContent = data.camera_type || 'Unknown';
                document.getElementById('model-status').textContent = data.model_loaded ? 'Loaded ✓' : 'Not Loaded ✗';
                document.getElementById('hardware-status').textContent = data.hardware_available ? 'Enabled ✓' : 'Disabled ✗';
            })
            .catch(err => console.error('Health check error:', err));
        
        // Auto-detect every 100ms (10 FPS)
        setInterval(autoDetect, 100);
        
        // Initial detection
        autoDetect();
    </script>
</body>
</html>
"""

# ============================================================
# CAMERA INITIALIZATION
# ============================================================

def initialize_picamera2():
    """Initialize Raspberry Pi Camera Module using picamera2"""
    try:
        from picamera2 import Picamera2
        
        cam = Picamera2()
        config = cam.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        cam.configure(config)
        cam.start()
        
        logger.info("✅ Raspberry Pi Camera Module initialized (picamera2)")
        return cam, "picamera2"
    except Exception as e:
        logger.warning(f"picamera2 error: {e}")
        return None, None

def initialize_opencv_camera():
    """Initialize camera using OpenCV (USB webcam)"""
    try:
        # Try common USB webcam indices (0, 1 are most common)
        usb_indices = [0, 1, 8, 9, 2, 3, 4]
        for i in usb_indices:
            # Force V4L2 backend to avoid GStreamer issues
            cam = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if cam.isOpened():
                # Set properties BEFORE reading
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cam.set(cv2.CAP_PROP_FPS, 15)
                
                # Warm up camera - discard first few frames
                for _ in range(5):
                    ret, _ = cam.read()
                    if not ret:
                        break
                    time.sleep(0.1)
                
                # Final verification
                ret, test_frame = cam.read()
                if ret and test_frame is not None:
                    logger.info(f"✅ USB Camera initialized at /dev/video{i} (640x480 @ 15fps, V4L2)")
                    return cam, "opencv"
                cam.release()
        return None, None
    except Exception as e:
        logger.warning(f"OpenCV camera error: {e}")
        return None, None

def initialize_camera():
    """Initialize camera - try USB webcam first, then picamera2"""
    global camera, camera_type
    
    # Try USB camera first (faster if webcam is connected)
    camera, camera_type = initialize_opencv_camera()
    if camera:
        return True
    
    # Fallback to Pi Camera
    camera, camera_type = initialize_picamera2()
    if camera:
        return True
    
    logger.error("❌ No camera found!")
    return False

# ============================================================
# MODEL INITIALIZATION
# ============================================================

def initialize_model():
    """Initialize TFLite model"""
    global interpreter, input_details, output_details, face_cascade, eye_cascade
    
    try:
        # Try different TFLite interpreter imports
        Interpreter = None
        try:
            from tflite_runtime.interpreter import Interpreter
            logger.info("Using tflite-runtime")
        except ImportError:
            try:
                from tensorflow.lite.python.interpreter import Interpreter
                logger.info("Using tensorflow.lite")
            except ImportError:
                try:
                    from ai_edge_litert.interpreter import Interpreter
                    logger.info("Using ai_edge_litert (TF 2.19+)")
                except ImportError:
                    logger.error("❌ No TFLite interpreter found!")
                    return False
        
        import os
        model_path = os.path.join(os.path.dirname(__file__), 'best_model_compatible.tflite')
        
        if not os.path.exists(model_path):
            logger.error(f"❌ Model file not found: {model_path}")
            return False
        
        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        logger.info(f"✅ Model loaded: {model_path}")
        logger.info(f"   Input shape: {input_details[0]['shape']}")
        
        # Load face cascade
        cascade_paths = [
            '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
            '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
        ]
        try:
            cascade_paths.append(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except:
            pass
        
        face_cascade = None
        for cascade_path in cascade_paths:
            if os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                if not face_cascade.empty():
                    logger.info(f"✅ Face cascade loaded from: {cascade_path}")
                    break
        
        if face_cascade is None or face_cascade.empty():
            logger.error("❌ Face cascade not found!")
            return False
        
        # Load eye cascade
        eye_cascade_paths = [
            '/usr/share/opencv4/haarcascades/haarcascade_eye.xml',
            '/usr/share/opencv/haarcascades/haarcascade_eye.xml'
        ]
        try:
            eye_cascade_paths.append(cv2.data.haarcascades + 'haarcascade_eye.xml')
        except:
            pass
        
        for eye_path in eye_cascade_paths:
            if os.path.exists(eye_path):
                eye_cascade = cv2.CascadeClassifier(eye_path)
                if not eye_cascade.empty():
                    logger.info(f"✅ Eye cascade loaded from: {eye_path}")
                    break
        
        if eye_cascade is None or eye_cascade.empty():
            logger.warning("⚠️ Eye cascade not found - will only show face box")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# HARDWARE ALERT CLASS
# ============================================================

class HardwareAlert:
    """Hardware alert with buzzer and RGB LED"""
    
    BUZZER_PIN = 17
    LED_RED_PIN = 22
    LED_GREEN_PIN = 27
    LED_BLUE_PIN = 24
    
    def __init__(self):
        if not GPIO_AVAILABLE:
            raise RuntimeError("GPIO not available")
        
        self.buzzer = Buzzer(self.BUZZER_PIN)
        self.led_r = PWMLED(self.LED_RED_PIN)
        self.led_g = PWMLED(self.LED_GREEN_PIN)
        self.led_b = PWMLED(self.LED_BLUE_PIN)
        self.buzzer_active = False
        
        logger.info("✅ Hardware initialized")
        logger.info(f"   Buzzer: GPIO{self.BUZZER_PIN}")
        logger.info(f"   RGB LED: R=GPIO{self.LED_RED_PIN}, G=GPIO{self.LED_GREEN_PIN}, B=GPIO{self.LED_BLUE_PIN}")
    
    def set_led(self, red=0, yellow=0, green=0):
        """Set individual LEDs (0=off, 100=on)"""
        self.led_r.value = red / 100.0
        self.led_g.value = yellow / 100.0
        self.led_b.value = green / 100.0
    
    def led_green(self):
        """Green only - Alert state"""
        self.set_led(red=0, yellow=0, green=100)
    
    def led_yellow(self):
        """Yellow only - Warning state"""
        self.set_led(red=0, yellow=100, green=0)
    
    def led_red(self):
        """Red only - Alarm state"""
        self.set_led(red=100, yellow=0, green=0)
    
    def led_off(self):
        """All LEDs off"""
        self.set_led(red=0, yellow=0, green=0)
    
    def buzzer_on(self):
        if not self.buzzer_active:
            self.buzzer.on()
            self.buzzer_active = True
    
    def buzzer_off(self):
        if self.buzzer_active:
            self.buzzer.off()
            self.buzzer_active = False
    
    def cleanup(self):
        try:
            self.buzzer.off()
            self.led_r.off()
            self.led_g.off()
            self.led_b.off()
        except:
            pass
        try:
            self.buzzer.close()
            self.led_r.close()
            self.led_g.close()
            self.led_b.close()
        except:
            pass
        logger.info("✅ GPIO cleaned up")

def initialize_hardware():
    """Initialize GPIO hardware"""
    global hardware
    
    if not GPIO_AVAILABLE:
        logger.warning("⚠️ GPIO not available - hardware alerts disabled")
        return False
    
    try:
        hardware = HardwareAlert()
        return True
    except Exception as e:
        logger.error(f"❌ Hardware init failed: {e}")
        return False

# ============================================================
# FRAME CAPTURE THREAD
# ============================================================

def capture_frames():
    """Capture frames in background thread"""
    global camera, output_frame, lock, camera_type, stop_capture_thread
    
    logger.info("🎥 Frame capture thread started")
    
    # Wait for camera to be ready
    max_wait = 10
    wait_count = 0
    while camera is None and wait_count < max_wait:
        time.sleep(0.1)
        wait_count += 0.1
    
    if camera is None:
        logger.error("Camera not initialized after waiting")
        return
    
    logger.info(f"Camera ready: type={camera_type}")
    
    consecutive_failures = 0
    max_consecutive_failures = 50  # Allow 50 consecutive failures before giving up
    
    while not stop_capture_thread:
        try:
            if camera_type == "picamera2":
                frame = camera.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                consecutive_failures = 0  # Reset on success
            else:
                # OpenCV camera
                if camera is None:
                    logger.warning("Camera object is None")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error("Too many consecutive failures, stopping capture thread")
                        break
                    time.sleep(0.5)
                    continue
                
                # Try to read frame
                ret, frame = camera.read()
                if not ret:
                    consecutive_failures += 1
                    logger.warning(f"Failed to read frame (attempt {consecutive_failures}/{max_consecutive_failures})")
                    
                    if consecutive_failures >= max_consecutive_failures:
                        logger.error("Too many consecutive failures, stopping capture thread")
                        break
                    
                    time.sleep(0.1)
                    continue
                
                # Success - reset failure counter
                consecutive_failures = 0
            
            with lock:
                output_frame = frame.copy()
                
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Capture error ({consecutive_failures}/{max_consecutive_failures}): {e}")
            
            if consecutive_failures >= max_consecutive_failures:
                logger.error("Too many consecutive errors, stopping capture thread")
                break
            
            time.sleep(0.1)
    
    logger.info("🎥 Frame capture thread stopped")

def generate_frames():
    """Generate frames for MJPEG streaming with bounding boxes"""
    global output_frame, lock
    
    last_frame_time = 0
    frame_interval = 1.0 / 15  # 15 FPS max
    
    while True:
        current_time = time.time()
        if current_time - last_frame_time < frame_interval:
            time.sleep(0.01)
            continue
        
        with lock:
            if output_frame is None:
                time.sleep(0.01)
                continue
            frame = output_frame.copy()
        
        # Draw bounding boxes
        frame = draw_bounding_boxes(frame)
        
        small = cv2.resize(frame, (480, 360))
        
        ret, buffer = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, 50])
        if not ret:
            continue
        
        last_frame_time = current_time
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# ============================================================
# BOUNDING BOX DRAWING
# ============================================================

def draw_bounding_boxes(frame):
    """Draw face and eye bounding boxes on frame"""
    global face_cascade, eye_cascade
    
    if face_cascade is None:
        return frame
    
    frame_with_boxes = frame.copy()
    gray = cv2.cvtColor(frame_with_boxes, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30)
    )
    
    for (x, y, w, h) in faces:
        # Draw face rectangle (green)
        cv2.rectangle(frame_with_boxes, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame_with_boxes, 'Face', (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Detect eyes
        if eye_cascade is not None:
            eye_region_height = int(h * 0.6)
            roi_gray = gray[y:y+eye_region_height, x:x+w]
            roi_color = frame_with_boxes[y:y+eye_region_height, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=10,
                minSize=(30, 30)
            )
            
            if len(eyes) > 0:
                eyes_sorted = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)
                eyes = eyes_sorted[:2]
                
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
            else:
                # Estimate eye positions when closed
                eye_width = int(w * 0.25)
                eye_height = int(h * 0.15)
                eye_y = int(eye_region_height * 0.4)
                
                left_eye_x = int(w * 0.2)
                cv2.rectangle(roi_color, 
                            (left_eye_x, eye_y), 
                            (left_eye_x + eye_width, eye_y + eye_height), 
                            (128, 128, 255), 2)
                
                right_eye_x = int(w * 0.55)
                cv2.rectangle(roi_color, 
                            (right_eye_x, eye_y), 
                            (right_eye_x + eye_width, eye_y + eye_height), 
                            (128, 128, 255), 2)
    
    return frame_with_boxes

# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_drowsiness(frame, threshold=0.65):
    """Predict drowsiness from frame"""
    global interpreter, input_details, output_details, face_cascade
    
    if interpreter is None or face_cascade is None:
        return False, None, None
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30)
    )
    
    if len(faces) == 0:
        return False, None, None
    
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    
    face_roi = frame[y:y+h, x:x+w]
    if face_roi.size == 0:
        return False, None, None
    
    face_roi = cv2.resize(face_roi, (224, 224))
    input_data = np.expand_dims(face_roi, axis=0)
    
    if input_details[0]['dtype'] == np.uint8:
        input_data = input_data.astype(np.uint8)
    else:
        input_data = input_data.astype(np.float32) / 255.0
    
    with inference_lock:
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index']).copy()
    
    if output_details[0]['dtype'] == np.uint8:
        quant_scale, zero_point = output_details[0]['quantization']
        confidence = (float(output[0][0]) - zero_point) * quant_scale
    else:
        confidence = float(output[0][0])
    
    # Lower confidence = drowsy (eyes closed)
    is_drowsy = confidence < threshold
    
    return True, is_drowsy, confidence

# ============================================================
# AUTO-DETECTION THREAD
# ============================================================

def auto_detection_loop():
    """Continuously detect drowsiness in background"""
    global output_frame, lock, current_state, state_lock, drowsy_start_time
    global hardware, stats, stop_detection_thread
    
    logger.info("🤖 Auto-detection thread started")
    
    # Initialize stats start time
    stats["start_time"] = time.time()
    
    while not stop_detection_thread:
        try:
            with lock:
                if output_frame is None:
                    time.sleep(0.1)
                    continue
                frame = output_frame.copy()
            
            face_detected, is_drowsy, confidence = predict_drowsiness(frame, threshold=0.65)
            
            current_time = time.time()
            alarm_active = False
            drowsy_duration = 0
            
            if not face_detected:
                drowsy_start_time = None
                if hardware:
                    hardware.led_off()
                    hardware.buzzer_off()
                
                with state_lock:
                    current_state.update({
                        "status": "NO FACE",
                        "is_drowsy": False,
                        "confidence": None,
                        "drowsy_duration": 0,
                        "alarm_active": False,
                        "face_detected": False
                    })
            else:
                # Update statistics
                stats["total_detections"] += 1
                
                if is_drowsy:
                    stats["drowsy_count"] += 1
                    
                    if drowsy_start_time is None:
                        drowsy_start_time = current_time
                        logger.info("⏱️ Drowsy state started")
                    
                    drowsy_duration = current_time - drowsy_start_time
                    
                    # Check if alarm should trigger
                    if drowsy_duration >= drowsy_duration_threshold:
                        alarm_active = True
                        logger.warning(f"⚠️ ALARM! Drowsy for {drowsy_duration:.1f}s")
                        if hardware:
                            hardware.led_red()
                            hardware.buzzer_on()
                    else:
                        logger.info(f"🔍 Drowsy duration: {drowsy_duration:.1f}s / {drowsy_duration_threshold}s")
                        if hardware:
                            hardware.led_yellow()
                            hardware.buzzer_off()
                else:
                    stats["alert_count"] += 1
                    
                    if drowsy_start_time is not None:
                        logger.info(f"✅ Alert state restored (was drowsy for {current_time - drowsy_start_time:.1f}s)")
                    drowsy_start_time = None
                    drowsy_duration = 0
                    if hardware:
                        hardware.led_green()
                        hardware.buzzer_off()
                
                with state_lock:
                    current_state.update({
                        "status": "DROWSY" if is_drowsy else "ALERT",
                        "is_drowsy": is_drowsy,
                        "confidence": confidence,
                        "drowsy_duration": drowsy_duration,
                        "alarm_active": alarm_active,
                        "face_detected": True
                    })
            
            # Sleep to maintain ~10 FPS detection rate
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Auto-detection error: {e}")
            time.sleep(0.1)
    
    logger.info("🤖 Auto-detection thread stopped")

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_status')
def get_status():
    """Get current detection status"""
    global current_state, state_lock, stats
    
    with state_lock:
        state_copy = current_state.copy()
    
    state_copy["stats"] = {
        "total": stats["total_detections"],
        "drowsy": stats["drowsy_count"],
        "alert": stats["alert_count"]
    }
    state_copy["alarm_threshold"] = drowsy_duration_threshold
    
    return jsonify(state_copy)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'camera_type': camera_type,
        'camera_active': camera is not None,
        'model_loaded': interpreter is not None,
        'face_cascade_loaded': face_cascade is not None,
        'hardware_available': hardware is not None
    })

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚗 AUTO DROWSINESS DETECTION SYSTEM")
    print("="*60)
    
    print(f"\n📦 Versions:")
    try:
        import tensorflow as tf
        print(f"   TensorFlow: {tf.__version__}")
    except ImportError:
        print(f"   TensorFlow: Not installed (using tflite-runtime)")
    try:
        import numpy as np
        print(f"   NumPy: {np.__version__}")
    except:
        pass
    print(f"   OpenCV: {cv2.__version__}")
    print()
    
    if not initialize_camera():
        print("\n⚠️  WARNING: Failed to initialize camera!")
        print("   App will run but video feed will not work.")
        print("   You can still access the web interface for troubleshooting.")
    else:
        print(f"\n✅ Camera Type: {camera_type}")
    
    if not initialize_model():
        print("\n⚠️ WARNING: Model failed to load!")
        print("   App will run but predictions will not work.")
    
    if initialize_hardware():
        print("✅ Hardware alerts enabled")
    else:
        print("⚠️ Hardware alerts disabled")
    
    
    # Start capture thread (only if camera is available)
    if camera is not None:
        capture_thread = threading.Thread(target=capture_frames, daemon=True)
        capture_thread.start()
        
        # Start auto-detection thread
        detection_thread = threading.Thread(target=auto_detection_loop, daemon=True)
        detection_thread.start()
        print("✅ Auto-detection enabled")
    else:
        print("⚠️  Auto-detection disabled (no camera)")
    
    print("✅ Model loaded" if interpreter else "⚠️  Model not loaded")
    print("\n" + "="*60)
    print("🌐 Open in browser: http://192.168.18.150:5000")
    print("="*60 + "\n")
    
    def cleanup():
        global hardware, camera, camera_type, stop_capture_thread, stop_detection_thread
        logger.info("Cleaning up...")
        
        stop_capture_thread = True
        stop_detection_thread = True
        time.sleep(0.5)
        
        if hardware:
            hardware.cleanup()
        if camera_type == "opencv" and camera:
            camera.release()
        elif camera_type == "picamera2" and camera:
            try:
                camera.stop()
                camera.close()
            except:
                pass
        logger.info("Cleanup complete")
    
    import atexit
    import signal
    
    atexit.register(cleanup)
    
    def signal_handler(sig, frame):
        print("\n\n⏹️  Stopping server...")
        cleanup()
        import sys
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped")
    finally:
        cleanup()
