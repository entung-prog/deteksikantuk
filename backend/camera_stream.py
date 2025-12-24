"""
Camera Streaming Server for Raspberry Pi
Supports both USB webcam and Raspberry Pi Camera Module (libcamera/picamera2)
"""

from flask import Flask, Response, render_template_string
import cv2
import threading
import numpy as np

app = Flask(__name__)

# Global variables
camera = None
output_frame = None
lock = threading.Lock()
camera_type = None

# HTML template
CAMERA_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Camera Stream</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 { color: #3b82f6; }
        img {
            max-width: 100%;
            border: 2px solid #3b82f6;
            border-radius: 8px;
        }
        .info {
            margin: 20px 0;
            padding: 15px;
            background: #2a2a2a;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <h1>📷 Raspberry Pi Camera Stream</h1>
    <div class="info">
        <p>Camera Type: {{ camera_type }}</p>
        <p>Stream URL: http://192.168.0.108:8080</p>
    </div>
    <img src="{{ url_for('video_feed') }}" />
</body>
</html>
"""

def initialize_picamera2():
    """Initialize Raspberry Pi Camera Module using picamera2 (libcamera)"""
    try:
        from picamera2 import Picamera2
        
        camera = Picamera2()
        # Configure for video streaming
        config = camera.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        camera.configure(config)
        camera.start()
        
        print("✅ Raspberry Pi Camera Module initialized (picamera2/libcamera)")
        return camera, "picamera2"
    except Exception as e:
        print(f"❌ picamera2 error: {e}")
        return None, None

def initialize_opencv_camera():
    """Initialize camera using OpenCV (USB or legacy)"""
    try:
        # Try USB camera first
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            print("✅ USB Camera initialized (OpenCV)")
            return cam, "opencv"
        
        # Try different indices
        for i in range(4):
            cam = cv2.VideoCapture(i)
            if cam.isOpened():
                cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print(f"✅ Camera initialized at index {i} (OpenCV)")
                return cam, "opencv"
        
        return None, None
    except Exception as e:
        print(f"❌ OpenCV camera error: {e}")
        return None, None

def initialize_camera():
    """Initialize camera - try picamera2 first, then OpenCV"""
    global camera, camera_type
    
    # Try Raspberry Pi Camera Module first
    camera, camera_type = initialize_picamera2()
    if camera:
        return True
    
    # Fall back to OpenCV (USB camera)
    camera, camera_type = initialize_opencv_camera()
    if camera:
        return True
    
    print("❌ No camera found!")
    return False

def capture_frames_picamera2():
    """Capture frames from picamera2"""
    global camera, output_frame, lock
    
    while True:
        try:
            # Capture frame as numpy array (already in RGB888)
            frame = camera.capture_array()
            
            # Convert RGB to BGR for OpenCV compatibility
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            with lock:
                output_frame = frame.copy()
        except Exception as e:
            print(f"Capture error: {e}")
            break

def capture_frames_opencv():
    """Capture frames from OpenCV camera"""
    global camera, output_frame, lock
    
    while True:
        if camera is None or not camera.isOpened():
            break
            
        ret, frame = camera.read()
        if not ret:
            continue
            
        with lock:
            output_frame = frame.copy()

def capture_frames():
    """Capture frames based on camera type"""
    if camera_type == "picamera2":
        capture_frames_picamera2()
    else:
        capture_frames_opencv()

def generate_frames():
    """Generate frames for streaming"""
    global output_frame, lock
    
    while True:
        with lock:
            if output_frame is None:
                continue
            frame = output_frame.copy()
        
        # Encode as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Camera view page"""
    return render_template_string(CAMERA_HTML, camera_type=camera_type or "Unknown")

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/health')
def health():
    """Health check"""
    return {'status': 'ok', 'camera_type': camera_type, 'camera_active': camera is not None}

if __name__ == '__main__':
    print("\n" + "="*60)
    print("📷 RASPBERRY PI CAMERA STREAMING SERVER")
    print("="*60)
    
    # Initialize camera
    if not initialize_camera():
        print("\n❌ Failed to initialize camera!")
        print("\nTroubleshooting:")
        print("1. For Pi Camera Module (libcamera):")
        print("   sudo apt install -y python3-picamera2")
        print("   Test: libcamera-hello --list-cameras")
        print("\n2. For USB Camera:")
        print("   Check: ls /dev/video*")
        print("   Install: sudo apt-get install python3-opencv")
        exit(1)
    
    # Start capture thread
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()
    
    print(f"\n✅ Camera Type: {camera_type}")
    print("\nCamera stream available at:")
    print("  - http://192.168.0.108:8080")
    print("  - http://localhost:8080")
    print("="*60 + "\n")
    
    # Start Flask server
    try:
        app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
    finally:
        if camera_type == "opencv" and camera:
            camera.release()
        elif camera_type == "picamera2" and camera:
            camera.stop()
            camera.close()
