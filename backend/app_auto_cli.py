#!/usr/bin/env python3
"""
Drowsiness Detection - CLI Auto-Detection Version
Runs in terminal with real-time status output
No web interface - just camera, detection, and GPIO feedback
"""

import sys
if '/usr/lib/python3/dist-packages' not in sys.path:
    sys.path.insert(0, '/usr/lib/python3/dist-packages')

import cv2
import numpy as np
import time
import os
from datetime import datetime

# ============================================================
# GLOBAL VARIABLES
# ============================================================
camera = None
camera_type = None
interpreter = None
input_details = None
output_details = None
face_cascade = None
hardware = None
GPIO_AVAILABLE = False

# Detection state
drowsy_start_time = None
drowsy_duration_threshold = 3.0  # seconds
stats = {
    "total": 0,
    "drowsy": 0,
    "alert": 0,
    "start_time": None
}

# Try to import GPIO
try:
    from gpiozero import Buzzer, PWMLED
    GPIO_AVAILABLE = True
    print("✅ GPIO library available")
except ImportError:
    print("⚠️  GPIO library not available - running without hardware alerts")

# ============================================================
# HARDWARE CLASS
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
        
        print(f"✅ Hardware initialized")
        print(f"   Buzzer: GPIO{self.BUZZER_PIN}")
        print(f"   RGB LED: R=GPIO{self.LED_RED_PIN}, G=GPIO{self.LED_GREEN_PIN}, B=GPIO{self.LED_BLUE_PIN}")
    
    def set_led(self, red=0, green=0, blue=0):
        """Set RGB LED (0-100)"""
        self.led_r.value = red / 100.0
        self.led_g.value = green / 100.0
        self.led_b.value = blue / 100.0
    
    def led_green(self):
        """Green - Alert state"""
        self.set_led(red=0, green=100, blue=0)
    
    def led_yellow(self):
        """Yellow - Warning state"""
        self.set_led(red=100, green=100, blue=0)
    
    def led_red(self):
        """Red - Alarm state"""
        self.set_led(red=100, green=0, blue=0)
    
    def led_off(self):
        """All LEDs off"""
        self.set_led(red=0, green=0, blue=0)
    
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
            self.buzzer.close()
            self.led_r.close()
            self.led_g.close()
            self.led_b.close()
        except:
            pass

# ============================================================
# CAMERA INITIALIZATION
# ============================================================
def initialize_camera():
    """Initialize camera - try USB first, then Pi Camera"""
    global camera, camera_type
    
    # Try USB camera
    try:
        usb_indices = [0, 1, 8, 9, 2, 3, 4]
        for i in usb_indices:
            cam = cv2.VideoCapture(i)
            if cam.isOpened():
                ret, _ = cam.read()
                if ret:
                    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    cam.set(cv2.CAP_PROP_FPS, 15)
                    camera = cam
                    camera_type = "opencv"
                    print(f"✅ USB Camera initialized at /dev/video{i}")
                    return True
                cam.release()
    except Exception as e:
        print(f"⚠️  USB camera error: {e}")
    
    # Try Pi Camera
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        config = cam.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        cam.configure(config)
        cam.start()
        camera = cam
        camera_type = "picamera2"
        print("✅ Raspberry Pi Camera Module initialized")
        return True
    except Exception as e:
        print(f"⚠️  Pi Camera error: {e}")
    
    print("❌ No camera found!")
    return False

# ============================================================
# MODEL INITIALIZATION
# ============================================================
def initialize_model():
    """Initialize TFLite model and face cascade"""
    global interpreter, input_details, output_details, face_cascade
    
    # Load TFLite interpreter
    try:
        Interpreter = None
        try:
            from tflite_runtime.interpreter import Interpreter
            print("Using tflite-runtime")
        except ImportError:
            try:
                from tensorflow.lite.python.interpreter import Interpreter
                print("Using tensorflow.lite")
            except ImportError:
                try:
                    from ai_edge_litert.interpreter import Interpreter
                    print("Using ai_edge_litert")
                except ImportError:
                    print("❌ No TFLite interpreter found!")
                    return False
        
        model_path = os.path.join(os.path.dirname(__file__), 'best_model_compatible.tflite')
        
        if not os.path.exists(model_path):
            print(f"❌ Model file not found: {model_path}")
            return False
        
        interpreter = Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        print(f"✅ Model loaded: {os.path.basename(model_path)}")
        print(f"   Input shape: {input_details[0]['shape']}")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False
    
    # Load face cascade
    cascade_paths = [
        '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
        '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml'
    ]
    try:
        cascade_paths.append(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    except:
        pass
    
    for cascade_path in cascade_paths:
        if os.path.exists(cascade_path):
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if not face_cascade.empty():
                print(f"✅ Face cascade loaded")
                return True
    
    print("❌ Face cascade not found!")
    return False

# ============================================================
# PREDICTION
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
    
    # Get largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    
    face_roi = frame[y:y+h, x:x+w]
    if face_roi.size == 0:
        return False, None, None
    
    # Preprocess
    face_roi = cv2.resize(face_roi, (224, 224))
    input_data = np.expand_dims(face_roi, axis=0)
    
    if input_details[0]['dtype'] == np.uint8:
        input_data = input_data.astype(np.uint8)
    else:
        input_data = input_data.astype(np.float32) / 255.0
    
    # Inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index']).copy()
    
    # Get confidence
    if output_details[0]['dtype'] == np.uint8:
        quant_scale, zero_point = output_details[0]['quantization']
        confidence = (float(output[0][0]) - zero_point) * quant_scale
    else:
        confidence = float(output[0][0])
    
    # Lower confidence = drowsy (eyes closed)
    is_drowsy = confidence < threshold
    
    return True, is_drowsy, confidence

# ============================================================
# MAIN LOOP
# ============================================================
def clear_line():
    """Clear current line in terminal"""
    print('\r' + ' ' * 100 + '\r', end='', flush=True)

def print_status(status, confidence, duration, stats_dict):
    """Print status on same line"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if status == "NO FACE":
        status_str = f"[{timestamp}] 🔍 NO FACE DETECTED"
        color = "\033[93m"  # Yellow
    elif status == "DROWSY":
        status_str = f"[{timestamp}] 😴 DROWSY | Conf: {confidence*100:.1f}% | Duration: {duration:.1f}s"
        if duration >= drowsy_duration_threshold:
            color = "\033[91m"  # Red
            status_str += " | ⚠️  ALARM!"
        else:
            color = "\033[93m"  # Yellow
    else:  # ALERT
        status_str = f"[{timestamp}] ✅ ALERT | Conf: {confidence*100:.1f}%"
        color = "\033[92m"  # Green
    
    reset = "\033[0m"
    stats_str = f" | Total: {stats_dict['total']} | Drowsy: {stats_dict['drowsy']} | Alert: {stats_dict['alert']}"
    
    clear_line()
    print(color + status_str + reset + stats_str, end='', flush=True)

def run_detection():
    """Main detection loop"""
    global camera, camera_type, hardware, drowsy_start_time, stats
    
    print("\n" + "="*80)
    print("🚗 DROWSINESS DETECTION - CLI MODE")
    print("="*80)
    print("\nInitializing...")
    
    # Initialize camera
    if not initialize_camera():
        print("❌ Failed to initialize camera!")
        return
    
    # Initialize model
    if not initialize_model():
        print("❌ Failed to initialize model!")
        return
    
    # Initialize hardware (optional)
    if GPIO_AVAILABLE:
        try:
            hardware = HardwareAlert()
        except Exception as e:
            print(f"⚠️  Hardware init failed: {e}")
            hardware = None
    
    print("\n" + "="*80)
    print("✅ SYSTEM READY - Starting detection...")
    print("Press Ctrl+C to stop")
    print("="*80 + "\n")
    
    stats["start_time"] = time.time()
    
    try:
        while True:
            # Capture frame
            if camera_type == "picamera2":
                frame = camera.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                ret, frame = camera.read()
                if not ret:
                    print("\n❌ Failed to read frame")
                    time.sleep(0.1)
                    continue
            
            # Predict
            face_detected, is_drowsy, confidence = predict_drowsiness(frame, threshold=0.65)
            
            current_time = time.time()
            duration = 0
            
            if not face_detected:
                # No face
                drowsy_start_time = None
                if hardware:
                    hardware.led_off()
                    hardware.buzzer_off()
                print_status("NO FACE", None, 0, stats)
                
            elif is_drowsy:
                # Drowsy detected
                stats["total"] += 1
                stats["drowsy"] += 1
                
                if drowsy_start_time is None:
                    drowsy_start_time = current_time
                
                duration = current_time - drowsy_start_time
                
                # Check alarm threshold
                if duration >= drowsy_duration_threshold:
                    # ALARM!
                    if hardware:
                        hardware.led_red()
                        hardware.buzzer_on()
                else:
                    # Warning
                    if hardware:
                        hardware.led_yellow()
                        hardware.buzzer_off()
                
                print_status("DROWSY", confidence, duration, stats)
                
            else:
                # Alert (awake)
                stats["total"] += 1
                stats["alert"] += 1
                
                drowsy_start_time = None
                if hardware:
                    hardware.led_green()
                    hardware.buzzer_off()
                
                print_status("ALERT", confidence, 0, stats)
            
            # Control detection rate (~10 FPS)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping detection...")
    finally:
        # Cleanup
        print("\nCleaning up...")
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
        
        # Print summary
        runtime = time.time() - stats["start_time"]
        print("\n" + "="*80)
        print("📊 SESSION SUMMARY")
        print("="*80)
        print(f"Runtime: {runtime:.1f}s")
        print(f"Total detections: {stats['total']}")
        print(f"Drowsy: {stats['drowsy']} ({stats['drowsy']/max(stats['total'],1)*100:.1f}%)")
        print(f"Alert: {stats['alert']} ({stats['alert']/max(stats['total'],1)*100:.1f}%)")
        print("="*80)
        print("✅ Done!\n")

if __name__ == "__main__":
    run_detection()
