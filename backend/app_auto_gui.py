#!/usr/bin/env python3
"""
Drowsiness Detection - GUI Auto-Detection Version
Displays camera preview in OpenCV window with real-time status
Features: Camera preview, bounding boxes, status overlay, LED indicators
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
eye_cascade = None
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

# Display settings
WINDOW_NAME = "Drowsiness Detection - Auto Mode"
paused = False

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
    global interpreter, input_details, output_details, face_cascade, eye_cascade
    
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
                break
    
    if face_cascade is None or face_cascade.empty():
        print("❌ Face cascade not found!")
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
                print(f"✅ Eye cascade loaded")
                break
    
    if eye_cascade is None or eye_cascade.empty():
        print("⚠️  Eye cascade not found - will only show face box")
    
    return True

# ============================================================
# PREDICTION
# ============================================================
def predict_drowsiness(frame, threshold=0.65):
    """Predict drowsiness from frame"""
    global interpreter, input_details, output_details, face_cascade
    
    if interpreter is None or face_cascade is None:
        return False, None, None, None
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30)
    )
    
    if len(faces) == 0:
        return False, None, None, None
    
    # Get largest face
    face_box = max(faces, key=lambda f: f[2] * f[3])
    x, y, w, h = face_box
    
    face_roi = frame[y:y+h, x:x+w]
    if face_roi.size == 0:
        return False, None, None, None
    
    # Preprocess
    face_roi_resized = cv2.resize(face_roi, (224, 224))
    input_data = np.expand_dims(face_roi_resized, axis=0)
    
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
    
    return True, is_drowsy, confidence, face_box

# ============================================================
# DRAWING FUNCTIONS
# ============================================================
def draw_bounding_boxes(frame, face_box):
    """Draw face and eye bounding boxes"""
    global eye_cascade
    
    if face_box is None:
        return frame
    
    x, y, w, h = face_box
    
    # Draw face rectangle (green)
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(frame, 'Face', (x, y-10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Detect and draw eyes
    if eye_cascade is not None:
        face_roi = frame[y:y+h, x:x+w]
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Only search in upper 60% of face
        eye_region_height = int(h * 0.6)
        eye_roi = gray_roi[0:eye_region_height, :]
        
        eyes = eye_cascade.detectMultiScale(
            eye_roi,
            scaleFactor=1.1,
            minNeighbors=8,
            minSize=(20, 20)
        )
        
        # Draw eye boxes (cyan)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 255, 0), 2)
    
    return frame

def draw_status_overlay(frame, status, confidence, duration, led_state):
    """Draw status information overlay on frame"""
    h, w = frame.shape[:2]
    
    # Create semi-transparent overlay
    overlay = frame.copy()
    
    # Status badge at top
    if status == "NO FACE":
        color = (128, 128, 128)  # Gray
        text = "NO FACE DETECTED"
    elif status == "DROWSY":
        if duration >= drowsy_duration_threshold:
            color = (0, 0, 255)  # Red - ALARM
            text = "DROWSY - ALARM!"
        else:
            color = (0, 165, 255)  # Orange - WARNING
            text = "DROWSY - WARNING"
    else:  # ALERT
        color = (0, 255, 0)  # Green
        text = "ALERT - AWAKE"
    
    # Draw status badge
    cv2.rectangle(overlay, (10, 10), (w-10, 70), (0, 0, 0), -1)
    cv2.rectangle(overlay, (10, 10), (w-10, 70), color, 3)
    cv2.putText(overlay, text, (20, 50),
               cv2.FONT_HERSHEY_BOLD, 1.2, color, 3)
    
    # Confidence and duration
    if confidence is not None:
        conf_text = f"Confidence: {confidence*100:.1f}%"
        cv2.putText(overlay, conf_text, (20, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    if status == "DROWSY":
        dur_text = f"Duration: {duration:.1f}s"
        dur_color = (0, 255, 0) if duration < 1.5 else (0, 165, 255) if duration < 3.0 else (0, 0, 255)
        cv2.putText(overlay, dur_text, (20, 130),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, dur_color, 2)
    
    # LED indicators at bottom
    led_y = h - 80
    cv2.rectangle(overlay, (10, led_y), (w-10, h-10), (0, 0, 0), -1)
    cv2.rectangle(overlay, (10, led_y), (w-10, h-10), (100, 100, 100), 2)
    
    cv2.putText(overlay, "LED Status:", (20, led_y + 25),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw LED circles
    led_x = 150
    led_radius = 15
    
    # Green LED
    green_color = (0, 255, 0) if led_state == "green" else (0, 80, 0)
    cv2.circle(overlay, (led_x, led_y + 35), led_radius, green_color, -1)
    cv2.putText(overlay, "Alert", (led_x - 20, led_y + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Yellow LED
    yellow_color = (0, 255, 255) if led_state == "yellow" else (0, 80, 80)
    cv2.circle(overlay, (led_x + 80, led_y + 35), led_radius, yellow_color, -1)
    cv2.putText(overlay, "Warning", (led_x + 55, led_y + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Red LED
    red_color = (0, 0, 255) if led_state == "red" else (0, 0, 80)
    cv2.circle(overlay, (led_x + 160, led_y + 35), led_radius, red_color, -1)
    cv2.putText(overlay, "Alarm", (led_x + 140, led_y + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Statistics
    stats_x = w - 250
    cv2.putText(overlay, f"Total: {stats['total']}", (stats_x, led_y + 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(overlay, f"Drowsy: {stats['drowsy']}", (stats_x, led_y + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(overlay, f"Alert: {stats['alert']}", (stats_x, led_y + 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Blend overlay
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Controls hint
    cv2.putText(frame, "ESC: Exit | SPACE: Pause", (10, h - 5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    return frame

# ============================================================
# MAIN LOOP
# ============================================================
def run_detection():
    """Main detection loop with GUI"""
    global camera, camera_type, hardware, drowsy_start_time, stats, paused
    
    print("\n" + "="*80)
    print("🚗 DROWSINESS DETECTION - GUI MODE")
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
    print("✅ SYSTEM READY - Opening preview window...")
    print("="*80)
    print("\nControls:")
    print("  ESC   - Exit application")
    print("  SPACE - Pause/Resume detection")
    print("="*80 + "\n")
    
    stats["start_time"] = time.time()
    
    # Create window
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 600)
    
    led_state = "off"
    fps_counter = 0
    fps_start = time.time()
    current_fps = 0
    
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
            
            if not paused:
                # Predict
                face_detected, is_drowsy, confidence, face_box = predict_drowsiness(frame, threshold=0.65)
                
                current_time = time.time()
                duration = 0
                
                if not face_detected:
                    # No face
                    status = "NO FACE"
                    drowsy_start_time = None
                    led_state = "off"
                    if hardware:
                        hardware.led_off()
                        hardware.buzzer_off()
                    
                elif is_drowsy:
                    # Drowsy detected
                    status = "DROWSY"
                    stats["total"] += 1
                    stats["drowsy"] += 1
                    
                    if drowsy_start_time is None:
                        drowsy_start_time = current_time
                    
                    duration = current_time - drowsy_start_time
                    
                    # Check alarm threshold
                    if duration >= drowsy_duration_threshold:
                        # ALARM!
                        led_state = "red"
                        if hardware:
                            hardware.led_red()
                            hardware.buzzer_on()
                    else:
                        # Warning
                        led_state = "yellow"
                        if hardware:
                            hardware.led_yellow()
                            hardware.buzzer_off()
                    
                else:
                    # Alert (awake)
                    status = "ALERT"
                    stats["total"] += 1
                    stats["alert"] += 1
                    
                    drowsy_start_time = None
                    led_state = "green"
                    if hardware:
                        hardware.led_green()
                        hardware.buzzer_off()
                
                # Draw bounding boxes
                if face_box is not None:
                    frame = draw_bounding_boxes(frame, face_box)
                
                # Draw status overlay
                frame = draw_status_overlay(frame, status, confidence, duration, led_state)
            else:
                # Paused
                cv2.putText(frame, "PAUSED", (frame.shape[1]//2 - 100, frame.shape[0]//2),
                           cv2.FONT_HERSHEY_BOLD, 2, (0, 0, 255), 4)
            
            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            # Draw FPS
            cv2.putText(frame, f"FPS: {current_fps}", (frame.shape[1] - 100, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Show frame
            cv2.imshow(WINDOW_NAME, frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                paused = not paused
                if paused:
                    print("\n⏸️  Detection PAUSED")
                else:
                    print("\n▶️  Detection RESUMED")
            
            # Control detection rate
            time.sleep(0.03)  # ~30 FPS max
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping detection...")
    finally:
        # Cleanup
        print("\nCleaning up...")
        cv2.destroyAllWindows()
        
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
