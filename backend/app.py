"""
Drowsiness Detection - Single Server Application (FIXED)
All-in-one: Camera Stream + Web UI + ML Prediction
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
eye_cascade = None  # For eye detection visualization
inference_lock = threading.Lock()
stop_capture_thread = False  # Flag to stop capture thread gracefully

# Drowsy duration tracking
drowsy_start_time = None
drowsy_duration_threshold = 3.0  # seconds (configurable)

# GPIO Hardware
hardware = None
GPIO_AVAILABLE = False

# Live Test Results Tracking (Real-time)
live_test_stats = {
    "total_detections": 0,
    "drowsy_detected": 0,
    "alert_detected": 0,
    "start_time": None,
    "inference_times": [],  # Track inference times
    "current_scenario": "Real-time Testing",  # User can set this
    "ground_truth_labels": []  # User will mark ground truth for accuracy calculation
}

# Scenario-based testing results (from Bab 4 - for reference/comparison)
REFERENCE_RESULTS = {
    "scenarios": [
        {"name": "Normal Driving", "condition": "Mata terbuka, pencahayaan normal", "duration": "5 menit", "true_positive": 0, "true_negative": 295, "false_positive": 5, "false_negative": 0, "accuracy": 0.9833},
        {"name": "Simulated Drowsiness", "condition": "Mata tertutup 2-3 detik berulang", "duration": "5 menit", "true_positive": 28, "true_negative": 0, "false_positive": 0, "false_negative": 2, "accuracy": 0.9333},
        {"name": "Blinking", "condition": "Kedipan normal (0.3-0.5 detik)", "duration": "3 menit", "true_positive": 0, "true_negative": 178, "false_positive": 2, "false_negative": 0, "accuracy": 0.9889},
        {"name": "Low Light", "condition": "Pencahayaan rendah (malam)", "duration": "3 menit", "true_positive": 15, "true_negative": 165, "false_positive": 8, "false_negative": 2, "accuracy": 0.9474},
        {"name": "Bright Light", "condition": "Pencahayaan tinggi (siang)", "duration": "3 menit", "true_positive": 14, "true_negative": 172, "false_positive": 6, "false_negative": 3, "accuracy": 0.9538}
    ]
}

# Try to import GPIO library
try:
    from gpiozero import Buzzer, PWMLED
    GPIO_AVAILABLE = True
    logger.info("GPIO library (gpiozero) available")
except ImportError:
    logger.warning("GPIO library not available - running without hardware alerts")

# ============================================================
# HTML TEMPLATE (Embedded) - FIXED ESCAPING
# ============================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚗 Drowsiness Detection System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        header p {
            color: #94a3b8;
            margin-top: 10px;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
        }
        
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
        }
        
        .video-section {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .video-container {
            position: relative;
            width: 100%;
            aspect-ratio: 4/3;
            background: #000;
            border-radius: 12px;
            overflow: hidden;
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
        }
        
        .status-badge {
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .status-alert {
            background: linear-gradient(135deg, #10b981, #059669);
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
        }
        
        .status-drowsy {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
            animation: pulse 1s infinite;
        }
        
        .status-noface {
            background: linear-gradient(135deg, #6b7280, #4b5563);
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .confidence-badge {
            background: rgba(0,0,0,0.7);
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .fps-badge {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            padding: 8px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        
        .controls {
            margin-top: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
        }
        
        .btn-primary.active {
            background: linear-gradient(135deg, #ef4444, #dc2626);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .btn-secondary:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .side-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .panel-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .panel-card h3 {
            font-size: 1rem;
            color: #94a3b8;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        .stat-item {
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #00d4ff;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #94a3b8;
            margin-top: 5px;
        }
        
        .setting-item {
            margin-bottom: 15px;
        }
        
        .setting-item label {
            display: block;
            font-size: 0.85rem;
            color: #94a3b8;
            margin-bottom: 8px;
        }
        
        .setting-item input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(255,255,255,0.1);
            appearance: none;
        }
        
        .setting-item input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #3b82f6;
            cursor: pointer;
        }
        
        .setting-item input[type="number"] {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 1rem;
        }
        
        .results-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        
        .results-table th, .results-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .results-table th {
            color: #94a3b8;
            font-weight: 500;
        }
        
        .badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-alert { background: #10b981; }
        .badge-drowsy { background: #ef4444; }
        
        .alarm-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(239, 68, 68, 0.3);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: flash 0.5s infinite;
        }
        
        .alarm-overlay.hidden { display: none; }
        
        .alarm-text {
            font-size: 4rem;
            font-weight: bold;
            text-shadow: 0 0 30px rgba(255,255,255,0.8);
        }
        
        @keyframes flash {
            0%, 100% { background: rgba(239, 68, 68, 0.3); }
            50% { background: rgba(239, 68, 68, 0.6); }
        }
        
        .table-scroll {
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚗 Drowsiness Detection System</h1>
            <p>Real-time Eye Closure Detection with AI</p>
        </header>
        
        <div class="main-grid">
            <div class="video-section">
                <div class="video-container">
                    <img id="video-stream" src="/video_feed" alt="Camera Stream">
                    
                    <div class="status-overlay">
                        <div id="status-badge" class="status-badge status-noface">NO FACE</div>
                        <div id="confidence-badge" class="confidence-badge">Confidence: --</div>
                    </div>
                    
                    <div id="fps-badge" class="fps-badge">FPS: --</div>
                </div>
                
                <div class="controls">
                    <button id="btn-detect" class="btn btn-primary">
                        <span>▶️</span> Start Detection
                    </button>
                    <button id="btn-capture" class="btn btn-secondary">
                        <span>📸</span> Capture Image
                    </button>
                    <button id="btn-export" class="btn btn-secondary">
                        <span>💾</span> Export Test Data
                    </button>
                    <button id="btn-clear" class="btn btn-secondary">
                        <span>🗑️</span> Clear
                    </button>
                </div>
                
                <div style="margin-top:15px;background:rgba(255,255,255,0.05);padding:15px;border-radius:12px">
                    <label style="display:block;color:#94a3b8;font-size:0.85rem;margin-bottom:8px">Scenario Name (for export)</label>
                    <select id="scenario-select" style="width:100%;padding:10px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(0,0,0,0.3);color:white;font-size:1rem">
                        <option value="normal_driving">Normal Driving</option>
                        <option value="simulated_drowsiness">Simulated Drowsiness</option>
                        <option value="blinking">Blinking</option>
                        <option value="low_light">Low Light</option>
                        <option value="bright_light">Bright Light</option>
                        <option value="custom">Custom Test</option>
                    </select>
                </div>
            </div>
            
            <div class="side-panel">
                <div class="panel-card">
                    <h3>📊 Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div id="total-detections" class="stat-value">0</div>
                            <div class="stat-label">Detections</div>
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
                            <div id="drowsy-duration" class="stat-value">0.0s</div>
                            <div class="stat-label">Duration</div>
                        </div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <h3>⚙️ Settings</h3>
                    <div class="setting-item">
                        <label>Drowsy Threshold: <span id="threshold-value">0.65</span></label>
                        <input type="range" id="threshold" min="0.1" max="0.9" step="0.05" value="0.65">
                    </div>
                    <div class="setting-item">
                        <label>Alarm Duration (seconds)</label>
                        <input type="number" id="alarm-duration" min="1" max="10" value="3">
                    </div>
                </div>
                
                <div class="panel-card">
                    <h3>📋 Recent Results</h3>
                    <div class="table-scroll">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Status</th>
                                    <th>Conf</th>
                                </tr>
                            </thead>
                            <tbody id="results-body">
                                <tr><td colspan="3" style="text-align:center;color:#666">No data yet</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="panel-card">
                    <h3>🧪 Live Test Results</h3>
                    <div style="font-size:0.85rem">
                        <div style="display:flex;justify-content:space-between;padding:10px 0">
                            <span style="color:#94a3b8">Total Samples</span>
                            <span style="color:#00d4ff;font-weight:bold" id="test-acc">--</span>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0">
                            <div style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;text-align:center">
                                <div style="font-size:1.3rem;color:#00d4ff;font-weight:bold" id="test-tp">--</div>
                                <div style="font-size:0.7rem;color:#94a3b8;margin-top:3px">Drowsy</div>
                            </div>
                            <div style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;text-align:center">
                                <div style="font-size:1.3rem;color:#00d4ff;font-weight:bold" id="test-tn">--</div>
                                <div style="font-size:0.7rem;color:#94a3b8;margin-top:3px">Alert</div>
                            </div>
                            <div style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;text-align:center">
                                <div style="font-size:1.3rem;color:#00d4ff;font-weight:bold" id="test-fp">--</div>
                                <div style="font-size:0.7rem;color:#94a3b8;margin-top:3px">FP</div>
                            </div>
                            <div style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;text-align:center">
                                <div style="font-size:1.3rem;color:#00d4ff;font-weight:bold" id="test-fn">--</div>
                                <div style="font-size:0.7rem;color:#94a3b8;margin-top:3px">FN</div>
                            </div>
                        </div>
                        <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:10px;margin-top:10px">
                            <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;margin-bottom:8px">Live Performance</div>
                            <div style="display:flex;justify-content:space-between;padding:5px 0;font-size:0.8rem">
                                <span style="color:#94a3b8">Avg Inference</span>
                                <span style="color:#fff" id="test-inf">--</span>
                            </div>
                            <div style="display:flex;justify-content:space-between;padding:5px 0;font-size:0.8rem">
                                <span style="color:#94a3b8">Est. FPS</span>
                                <span style="color:#fff" id="test-fps">--</span>
                            </div>
                        </div>
                        <button id="btn-scenarios" style="width:100%;margin-top:10px;padding:10px;background:rgba(59,130,246,0.2);border:1px solid rgba(59,130,246,0.4);border-radius:8px;color:#3b82f6;font-size:0.8rem;cursor:pointer">
                            📊 View Reference Data (Bab 4)
                        </button>
                        <div id="scenarios-panel" style="display:none;margin-top:10px;max-height:300px;overflow-y:auto"></div>
                    </div>
                </div>
                
                <div class="panel-card">
                    <h3>📊 Resource Usage (RPi 5)</h3>
                    <div style="font-size:0.85rem">
                        <div style="display:flex;justify-content:space-between;padding:8px 0">
                            <span style="color:#94a3b8">CPU</span>
                            <span style="color:#00d4ff;font-weight:bold" id="res-cpu">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;padding:8px 0">
                            <span style="color:#94a3b8">RAM</span>
                            <span style="color:#00d4ff;font-weight:bold" id="res-ram">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;padding:8px 0">
                            <span style="color:#94a3b8">Temperature</span>
                            <span style="color:#00d4ff;font-weight:bold" id="res-temp">--</span>
                        </div>
                        <div style="display:flex;justify-content:space-between;padding:8px 0">
                            <span style="color:#94a3b8">Power</span>
                            <span style="color:#00d4ff;font-weight:bold" id="res-power">--</span>
                        </div>
                        <div style="margin-top:10px;padding:10px;background:rgba(59,130,246,0.1);border-radius:8px;font-size:0.75rem;color:#94a3b8;text-align:center">
                            Auto-updates every 5s
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
        let isDetecting = false;
        let detectionInterval = null;
        let results = [];
        let drowsyStartTime = null;
        let currentDrowsyDuration = 0;
        let lastFpsTime = Date.now();
        let frameCount = 0;
        let isProcessing = false;
        
        const btnDetect = document.getElementById('btn-detect');
        const btnExport = document.getElementById('btn-export');
        const btnClear = document.getElementById('btn-clear');
        const statusBadge = document.getElementById('status-badge');
        const confidenceBadge = document.getElementById('confidence-badge');
        const fpsBadge = document.getElementById('fps-badge');
        const thresholdInput = document.getElementById('threshold');
        const thresholdValue = document.getElementById('threshold-value');
        const alarmDurationInput = document.getElementById('alarm-duration');
        const alarmOverlay = document.getElementById('alarm-overlay');
        const resultsBody = document.getElementById('results-body');
        
        const totalDetections = document.getElementById('total-detections');
        const drowsyCount = document.getElementById('drowsy-count');
        const alertCount = document.getElementById('alert-count');
        const drowsyDuration = document.getElementById('drowsy-duration');
        
        const btnCapture = document.getElementById('btn-capture');
        
        btnDetect.addEventListener('click', toggleDetection);
        btnCapture.addEventListener('click', captureFrame);
        btnExport.addEventListener('click', exportResults);
        btnClear.addEventListener('click', clearResults);
        thresholdInput.addEventListener('input', (e) => {
            thresholdValue.textContent = parseFloat(e.target.value).toFixed(2);
        });
        
        function toggleDetection() {
            isDetecting = !isDetecting;
            
            if (isDetecting) {
                btnDetect.innerHTML = '<span>⏹️</span> Stop Detection';
                btnDetect.classList.add('active');
                startDetection();
            } else {
                btnDetect.innerHTML = '<span>▶️</span> Start Detection';
                btnDetect.classList.remove('active');
                stopDetection();
            }
        }
        
        function startDetection() {
            detectionInterval = setInterval(detect, 100);  // 10 FPS for real-time feel
        }
        
        function stopDetection() {
            if (detectionInterval) {
                clearInterval(detectionInterval);
                detectionInterval = null;
            }
            resetDrowsyState();
        }
        
        async function detect() {
            if (isProcessing) return;
            isProcessing = true;
            
            try {
                const threshold = parseFloat(thresholdInput.value);
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ threshold: threshold })
                });
                
                const data = await response.json();
                
                frameCount++;
                const now = Date.now();
                if (now - lastFpsTime >= 1000) {
                    fpsBadge.textContent = 'FPS: ' + frameCount;
                    frameCount = 0;
                    lastFpsTime = now;
                }
                
                if (!data.face_detected) {
                    updateStatus('NO FACE', null, false);
                    resetDrowsyState();
                    return;
                }
                
                if (data.confidence === null) {
                    updateStatus('NO EYES', null, false);
                    return;
                }
                
                updateDrowsyState(data.is_drowsy);
                
                updateStatus(
                    data.is_drowsy ? 'DROWSY' : 'ALERT',
                    data.confidence,
                    data.is_drowsy
                );
                
                addResult(data.is_drowsy, data.confidence);
                
            } catch (error) {
                console.error('Detection error:', error);
            } finally {
                isProcessing = false;
            }
        }
        
        function updateStatus(status, confidence, isDrowsy) {
            statusBadge.textContent = status;
            statusBadge.className = 'status-badge';
            
            if (status === 'ALERT') {
                statusBadge.classList.add('status-alert');
            } else if (status === 'DROWSY') {
                statusBadge.classList.add('status-drowsy');
            } else {
                statusBadge.classList.add('status-noface');
            }
            
            if (confidence !== null) {
                confidenceBadge.textContent = 'Confidence: ' + (confidence * 100).toFixed(1) + '%';
            } else {
                confidenceBadge.textContent = 'Confidence: --';
            }
        }
        
        function updateDrowsyState(isDrowsy) {
            if (isDrowsy) {
                if (drowsyStartTime === null) {
                    drowsyStartTime = Date.now();
                }
                currentDrowsyDuration = (Date.now() - drowsyStartTime) / 1000;
                drowsyDuration.textContent = currentDrowsyDuration.toFixed(1) + 's';
                
                const alarmDur = parseFloat(alarmDurationInput.value);
                if (currentDrowsyDuration >= alarmDur) {
                    alarmOverlay.classList.remove('hidden');
                }
            } else {
                resetDrowsyState();
            }
        }
        
        function resetDrowsyState() {
            drowsyStartTime = null;
            currentDrowsyDuration = 0;
            drowsyDuration.textContent = '0.0s';
            alarmOverlay.classList.add('hidden');
        }
        
        function addResult(isDrowsy, confidence) {
            const time = new Date().toLocaleTimeString('id-ID');
            results.push({
                time: time,
                status: isDrowsy ? 'Drowsy' : 'Alert',
                confidence: (confidence * 100).toFixed(1)
            });
            
            totalDetections.textContent = results.length;
            drowsyCount.textContent = results.filter(r => r.status === 'Drowsy').length;
            alertCount.textContent = results.filter(r => r.status === 'Alert').length;
            
            updateResultsTable();
        }
        
        function updateResultsTable() {
            const last10 = results.slice(-10).reverse();
            
            if (last10.length === 0) {
                resultsBody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:#666">No data yet</td></tr>';
                return;
            }
            
            resultsBody.innerHTML = last10.map(r => 
                '<tr><td>' + r.time + '</td><td><span class="badge ' + 
                (r.status === 'Drowsy' ? 'badge-drowsy' : 'badge-alert') + 
                '">' + r.status + '</span></td><td>' + r.confidence + '%</td></tr>'
            ).join('');
        }
        
        function exportResults() {
            const scenarioSelect = document.getElementById('scenario-select');
            const scenarioName = scenarioSelect.value;
            
            if (confirm(`Export test data for scenario: ${scenarioName}?`)) {
                fetch('/export_test_data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({scenario_name: scenarioName})
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        let message = `✅ Test data exported!\n\nCSV: ${data.filename}\nSamples: ${data.total_samples}`;
                        if (data.photo_filename) {
                            message += `\n📸 Photo: ${data.photo_filename}`;
                        }
                        message += `\n\nSaved to: test_results/`;
                        alert(message);
                    } else {
                        alert('❌ Export failed: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(err => {
                    console.error('Export error:', err);
                    alert('❌ Export failed: ' + err.message);
                });
            }
        }
        
        function clearResults() {
            if (confirm('Clear all test statistics?')) {
                fetch('/reset_test_stats', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        results = [];
                        totalDetections.textContent = '0';
                        drowsyCount.textContent = '0';
                        alertCount.textContent = '0';
                        updateResultsTable();
                        alert('✅ Statistics cleared!');
                    }
                })
                .catch(err => console.error('Clear error:', err));
            }
        }
        
        function captureFrame() {
            const scenarioSelect = document.getElementById('scenario-select');
            const scenarioName = scenarioSelect.value;
            
            fetch('/capture_frame', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({scenario_name: scenarioName})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Image captured!\n\nFilename: ${data.filename}\nSaved to: test_results/`);
                } else {
                    alert('❌ Capture failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(err => {
                console.error('Capture error:', err);
                alert('❌ Capture failed: ' + err.message);
            });
        }
        
        
        fetch('/health')
            .then(r => r.json())
            .then(data => {
                console.log('✅ Server ready:', data);
            })
            .catch(err => {
                console.error('❌ Server error:', err);
                alert('Cannot connect to server!');
            });
        
        
        // Load test results (live stats)
        function loadTestResults() {
            fetch('/test_results')
                .then(r => r.json())
                .then(data => {
                    // Show live stats instead of static accuracy
                    const total = data.live_stats.total_detections;
                    const drowsy = data.live_stats.drowsy_detected;
                    const alert = data.live_stats.alert_detected;
                    
                    document.getElementById('test-acc').textContent = total > 0 ? 
                        `${total} samples` : 'No data yet';
                    document.getElementById('test-tp').textContent = drowsy;
                    document.getElementById('test-tn').textContent = alert;
                    document.getElementById('test-fp').textContent = '-';
                    document.getElementById('test-fn').textContent = '-';
                    document.getElementById('test-inf').textContent = data.performance.inference_time_ms + ' ms';
                    document.getElementById('test-fps').textContent = data.performance.fps + ' FPS';
                    
                    // Scenarios button (shows reference data from Bab 4)
                    document.getElementById('btn-scenarios').onclick = function() {
                        const panel = document.getElementById('scenarios-panel');
                        if (panel.style.display === 'none') {
                            panel.innerHTML = data.scenarios.map(s => `
                                <div style="background:rgba(0,0,0,0.2);border-left:3px solid #3b82f6;padding:10px;margin-bottom:8px;border-radius:6px">
                                    <div style="font-weight:bold;color:#00d4ff;margin-bottom:3px">${s.name}</div>
                                    <div style="font-size:0.7rem;color:#94a3b8;margin-bottom:6px">${s.condition}</div>
                                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:0.75rem">
                                        <div><span style="color:#94a3b8">TP:</span> ${s.true_positive}</div>
                                        <div><span style="color:#94a3b8">TN:</span> ${s.true_negative}</div>
                                        <div><span style="color:#94a3b8">FP:</span> ${s.false_positive}</div>
                                        <div><span style="color:#94a3b8">FN:</span> ${s.false_negative}</div>
                                    </div>
                                    <div style="text-align:center;margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.1);color:#10b981;font-weight:bold">
                                        Accuracy: ${(s.accuracy * 100).toFixed(2)}%
                                    </div>
                                </div>
                            `).join('');
                            panel.style.display = 'block';
                            this.textContent = '📊 Hide Reference Data (Bab 4)';
                        } else {
                            panel.style.display = 'none';
                            this.textContent = '📊 View Reference Data (Bab 4)';
                        }
                    };
                })
                .catch(err => console.error('Failed to load test results:', err));
        }
        
        // Load initially
        loadTestResults();
        
        // Auto-refresh every 2 seconds to show live updates
        setInterval(loadTestResults, 2000);
        
        // Load resource stats
        function loadResourceStats() {
            fetch('/resource_stats')
                .then(r => r.json())
                .then(data => {
                    if (!data.error) {
                        document.getElementById('res-cpu').textContent = data.cpu_percent + '%';
                        document.getElementById('res-ram').textContent = data.ram_gb + ' GB';
                        document.getElementById('res-temp').textContent = data.temp_c + '°C';
                        document.getElementById('res-power').textContent = data.power_w + ' W';
                    }
                })
                .catch(err => console.error('Resource stats error:', err));
        }
        
        // Load resource stats initially and every 5 seconds
        loadResourceStats();
        setInterval(loadResourceStats, 5000);
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
        usb_indices = [8, 9, 0, 1, 2, 3, 4]
        for i in usb_indices:
            cam = cv2.VideoCapture(i)
            if cam.isOpened():
                ret, _ = cam.read()
                if ret:
                    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    cam.set(cv2.CAP_PROP_FPS, 15)
                    logger.info(f"✅ USB Camera initialized at /dev/video{i} (640x480 @ 15fps)")
                    return cam, "opencv"
                cam.release()
        return None, None
    except Exception as e:
        logger.warning(f"OpenCV camera error: {e}")
        return None, None

def initialize_camera():
    """Initialize camera - try USB webcam first, then picamera2"""
    global camera, camera_type
    
    camera, camera_type = initialize_opencv_camera()
    if camera:
        return True
    
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
    global interpreter, input_details, output_details, face_cascade
    
    try:
        # Try different TFLite interpreter imports (TF 2.19 compatibility)
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
                    # TF 2.19+ new location (though deprecated)
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
        
        # Load eye cascade for visualization
        global eye_cascade
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
        self.led_g.value = yellow / 100.0  # GPIO27 = Yellow LED
        self.led_b.value = green / 100.0   # GPIO24 = Green LED
    
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
    
    def update_status(self, is_drowsy, confidence):
        """Update hardware based on drowsy status"""
        if is_drowsy:
            self.led_red()
            self.buzzer_on()
        elif confidence is not None and confidence >= 0.3:
            self.led_yellow()
            self.buzzer_off()
        else:
            self.led_green()
            self.buzzer_off()
    
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
    max_wait = 10  # seconds
    wait_count = 0
    while camera is None and wait_count < max_wait:
        time.sleep(0.1)
        wait_count += 0.1
    
    if camera is None:
        logger.error("Camera not initialized after waiting")
        return
    
    
    # Check if camera is opened, if not try to re-open
    if camera_type == "opencv" and not camera.isOpened():
        logger.warning("Camera was closed, attempting to re-open...")
        # Try to find which device was used
        camera_reopened = False
        for i in [0, 8, 9, 1, 2]:
            test_cam = cv2.VideoCapture(i)
            if test_cam.isOpened():
                ret, _ = test_cam.read()
                if ret:
                    # Don't set properties - just use camera as-is to avoid GStreamer issues
                    camera = test_cam
                    camera_reopened = True
                    logger.info(f"✅ Camera re-opened on /dev/video{i}")
                    break
                test_cam.release()
        
        if not camera_reopened:
            logger.error("Failed to re-open camera")
            return
    
    logger.info(f"Camera ready: type={camera_type}, isOpened={camera.isOpened() if hasattr(camera, 'isOpened') else 'N/A'}")
    
    while not stop_capture_thread:
        try:
            if camera_type == "picamera2":
                frame = camera.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                if camera is None:
                    logger.warning("Camera became None during capture")
                    break
                if not camera.isOpened():
                    logger.warning("Camera not opened, stopping capture thread")
                    break
                ret, frame = camera.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    time.sleep(0.1)
                    continue
            
            with lock:
                output_frame = frame.copy()
                
        except Exception as e:
            logger.error(f"Capture error: {e}")
            time.sleep(0.1)
    
    logger.info("🎥 Frame capture thread stopped gracefully")

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
        
        # Draw bounding boxes using helper function
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
        
        # Add label
        cv2.putText(frame_with_boxes, 'Face', (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Detect eyes within face region
        if eye_cascade is not None:
            # Only detect in upper half of face (where eyes actually are)
            eye_region_height = int(h * 0.6)  # Top 60% of face
            roi_gray = gray[y:y+eye_region_height, x:x+w]
            roi_color = frame_with_boxes[y:y+eye_region_height, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=10,  # Increased from 5 to reduce false positives
                minSize=(30, 30)   # Increased minimum size
            )
            
            # Filter and select only the 2 largest detections (left and right eye)
            if len(eyes) > 0:
                # Sort by area (width * height) and take top 2
                eyes_sorted = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)
                eyes = eyes_sorted[:2]  # Only keep 2 largest
                
                for (ex, ey, ew, eh) in eyes:
                    # Draw eye rectangle (blue)
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
            else:
                # Fallback: Estimate eye positions when not detected (e.g., eyes closed)
                # Based on typical face proportions
                eye_width = int(w * 0.25)
                eye_height = int(h * 0.15)
                eye_y = int(eye_region_height * 0.4)  # 40% down from top of region
                
                # Left eye (from viewer's perspective)
                left_eye_x = int(w * 0.2)
                cv2.rectangle(roi_color, 
                            (left_eye_x, eye_y), 
                            (left_eye_x + eye_width, eye_y + eye_height), 
                            (128, 128, 255), 2)  # Light blue for estimated
                
                # Right eye
                right_eye_x = int(w * 0.55)
                cv2.rectangle(roi_color, 
                            (right_eye_x, eye_y), 
                            (right_eye_x + eye_width, eye_y + eye_height), 
                            (128, 128, 255), 2)  # Light blue for estimated
    
    return frame_with_boxes

# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_drowsiness(frame, threshold=0.5):
    """Predict drowsiness from frame"""
    global interpreter, input_details, output_details, face_cascade, live_test_stats
    
    if interpreter is None or face_cascade is None:
        logger.warning("Model or face cascade not initialized")
        return False, None, None, 0
    
    import time
    start_time = time.time()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30)
    )
    
    if len(faces) == 0:
        return False, None, None, 0
    
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    
    face_roi = frame[y:y+h, x:x+w]
    if face_roi.size == 0:
        return False, None, None, 0
    
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
    # Higher confidence = alert (eyes open)
    is_drowsy = confidence < threshold
    
    # Calculate inference time
    inference_time_ms = (time.time() - start_time) * 1000
    
    # Track inference time
    if len(live_test_stats["inference_times"]) < 100:  # Keep last 100
        live_test_stats["inference_times"].append(inference_time_ms)
    else:
        live_test_stats["inference_times"].pop(0)
        live_test_stats["inference_times"].append(inference_time_ms)
    
    # DEBUG: Log confidence values to help diagnose
    logger.info(f"🔍 DEBUG - Confidence: {confidence:.3f}, Threshold: {threshold:.2f}, Drowsy: {is_drowsy}, Inference: {inference_time_ms:.1f}ms")
    
    return True, is_drowsy, {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}, inference_time_ms


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

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint - uses current frame"""
    global output_frame, lock, hardware, drowsy_start_time, drowsy_duration_threshold, live_test_stats
    
    try:
        data = request.get_json() or {}
        threshold = data.get('threshold', 0.65)
        alarm_duration = data.get('alarm_duration', 3)  # Get from UI
        drowsy_duration_threshold = float(alarm_duration)
        
        with lock:
            if output_frame is None:
                return jsonify({'error': 'No frame available'}), 503
            frame = output_frame.copy()
        
        face_detected, is_drowsy, face_box, inference_time_ms = predict_drowsiness(frame, threshold)
        
        # Initialize start time if first detection
        if live_test_stats["start_time"] is None and face_detected:
            import time
            live_test_stats["start_time"] = time.time()
        
        # Track statistics
        if face_detected:
            live_test_stats["total_detections"] += 1
            if is_drowsy:
                live_test_stats["drowsy_detected"] += 1
            else:
                live_test_stats["alert_detected"] += 1
        
        if not face_detected:
            logger.info("🔍 DEBUG - No face detected")
            drowsy_start_time = None  # Reset timer
            if hardware:
                hardware.led_off()
                hardware.buzzer_off()
            return jsonify({
                'face_detected': False,
                'is_drowsy': None,
                'confidence': None,
                'drowsy_duration': 0,
                'alarm_active': False
            })
        
        # Duration-based alarm logic
        import time
        current_time = time.time()
        alarm_active = False
        drowsy_duration = 0
        
        if is_drowsy:
            if drowsy_start_time is None:
                drowsy_start_time = current_time
                logger.info("⏱️ Drowsy state started")
            
            drowsy_duration = current_time - drowsy_start_time
            
            # Only trigger alarm after threshold duration
            if drowsy_duration >= drowsy_duration_threshold:
                alarm_active = True
                logger.warning(f"⚠️ ALARM! Drowsy for {drowsy_duration:.1f}s (threshold: {drowsy_duration_threshold}s)")
                if hardware:
                    hardware.led_red()
                    hardware.buzzer_on()
            else:
                # Still drowsy but not long enough
                logger.info(f"🔍 Drowsy duration: {drowsy_duration:.1f}s / {drowsy_duration_threshold}s")
                if hardware:
                    hardware.led_yellow()  # Warning state
                    hardware.buzzer_off()
        else:
            # Alert state - reset timer
            if drowsy_start_time is not None:
                logger.info(f"✅ Alert state restored (was drowsy for {current_time - drowsy_start_time:.1f}s)")
            drowsy_start_time = None
            drowsy_duration = 0
            if hardware:
                hardware.led_green()
                hardware.buzzer_off()
        
        return jsonify({
            'face_detected': True,
            'is_drowsy': is_drowsy,
            'confidence': 0.5 if not is_drowsy else 0.3,  # Dummy value for UI
            'face_box': face_box,
            'drowsy_duration': round(drowsy_duration, 1),
            'alarm_active': alarm_active,
            'alarm_threshold': drowsy_duration_threshold
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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

@app.route('/test_results')
def test_results():
    """Get live test results"""
    global live_test_stats, REFERENCE_RESULTS
    
    import time
    
    # Calculate live statistics
    total = live_test_stats["total_detections"]
    drowsy = live_test_stats["drowsy_detected"]
    alert = live_test_stats["alert_detected"]
    
    # Calculate average inference time
    avg_inference = 0
    if live_test_stats["inference_times"]:
        avg_inference = sum(live_test_stats["inference_times"]) / len(live_test_stats["inference_times"])
    
    # Calculate FPS (approximate from inference time)
    fps = int(1000 / avg_inference) if avg_inference > 0 else 0
    
    # Calculate duration
    duration_seconds = 0
    if live_test_stats["start_time"]:
        duration_seconds = time.time() - live_test_stats["start_time"]
    
    return jsonify({
        "overall": {
            "accuracy": 0,  # Cannot calculate without ground truth
            "true_positive": 0,  # User needs to provide ground truth
            "true_negative": 0,
            "false_positive": 0,
            "false_negative": 0,
            "total_samples": total
        },
        "live_stats": {
            "total_detections": total,
            "drowsy_detected": drowsy,
            "alert_detected": alert,
            "duration_seconds": round(duration_seconds, 1),
            "current_scenario": live_test_stats["current_scenario"]
        },
        "performance": {
            "inference_time_ms": round(avg_inference, 1),
            "fps": fps,
            "latency_ms": round(avg_inference, 1)
        },
        "scenarios": REFERENCE_RESULTS["scenarios"]  # Reference data from Bab 4
    })

@app.route('/resource_stats')
def resource_stats():
    """Get current resource usage statistics"""
    try:
        import psutil
        import subprocess
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.5)
        
        # RAM
        memory = psutil.virtual_memory()
        ram_gb = memory.used / (1024 ** 3)
        
        # Temperature
        try:
            temp_output = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
            temp_c = float(temp_output.replace("temp=", "").replace("'C\n", ""))
        except:
            temp_c = 0.0
        
        # Power estimation (rough)
        base_power = 2.5
        max_power = 5.0
        estimated_power = base_power + (max_power - base_power) * (cpu_percent / 100)
        
        return jsonify({
            "cpu_percent": round(cpu_percent, 1),
            "ram_gb": round(ram_gb, 2),
            "temp_c": round(temp_c, 1),
            "power_w": round(estimated_power, 1)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export_test_data', methods=['POST'])
def export_test_data():
    """Export test data with enhanced CSV and metadata"""
    global live_test_stats
    
    try:
        data = request.get_json() or {}
        scenario_name = data.get('scenario_name', 'test')
        
        import csv
        import os
        from datetime import datetime
        
        # Create test_results directory if not exists
        results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"{scenario_name}_{timestamp}.csv"
        csv_path = os.path.join(results_dir, csv_filename)
        
        # Get resource stats (optional)
        cpu_percent = 0
        ram_gb = 0
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            ram_gb = memory.used / (1024 ** 3)
        except:
            pass  # Resource stats optional
        
        # Calculate statistics
        total = live_test_stats["total_detections"]
        drowsy = live_test_stats["drowsy_detected"]
        alert = live_test_stats["alert_detected"]
        avg_inference = 0
        if live_test_stats["inference_times"]:
            avg_inference = sum(live_test_stats["inference_times"]) / len(live_test_stats["inference_times"])
        
        # Calculate duration
        duration_seconds = 0
        if live_test_stats["start_time"]:
            import time
            duration_seconds = time.time() - live_test_stats["start_time"]
        
        # Write CSV
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header - Metadata
            writer.writerow(['# Test Results Export'])
            writer.writerow(['# Scenario', scenario_name])
            writer.writerow(['# Timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['# Duration', f"{round(duration_seconds, 1)} seconds"])
            writer.writerow([])
            
            # Summary Statistics
            writer.writerow(['Summary Statistics'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Detections', total])
            writer.writerow(['Drowsy Detected', drowsy])
            writer.writerow(['Alert Detected', alert])
            writer.writerow(['Avg Inference Time (ms)', round(avg_inference, 2)])
            writer.writerow([])
            
            # Resource Usage
            writer.writerow(['Resource Usage'])
            writer.writerow(['Resource', 'Value'])
            writer.writerow(['CPU Usage (%)', round(cpu_percent, 1)])
            writer.writerow(['RAM Usage (GB)', round(ram_gb, 2)])
            writer.writerow([])
            
            # Inference Times
            writer.writerow(['Inference Times (ms)'])
            writer.writerow(['Sample', 'Time (ms)'])
            for idx, inf_time in enumerate(live_test_stats["inference_times"], 1):
                writer.writerow([idx, round(inf_time, 2)])
        
        
        # Prepare response data
        response_data = {
            "success": True,
            "filename": csv_filename,
            "path": csv_path,
            "total_samples": total
        }
        
        # Auto-capture face photo with bounding boxes for documentation
        try:
            with lock:
                if output_frame is not None:
                    frame = output_frame.copy()
                    
                    # Draw bounding boxes on frame
                    frame_with_boxes = draw_bounding_boxes(frame)
                    
                    photo_filename = f"{scenario_name}_{timestamp}.jpg"
                    photo_path = os.path.join(results_dir, photo_filename)
                    cv2.imwrite(photo_path, frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    logger.info(f"📸 Face photo saved: {photo_filename}")
                    response_data["photo_filename"] = photo_filename
        except Exception as photo_error:
            logger.warning(f"Failed to save photo: {photo_error}")
        
        return jsonify(response_data)

        
    except Exception as e:
        logger.error(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/reset_test_stats', methods=['POST'])
def reset_test_stats():
    """Reset live test statistics"""
    global live_test_stats
    
    live_test_stats["total_detections"] = 0
    live_test_stats["drowsy_detected"] = 0
    live_test_stats["alert_detected"] = 0
    live_test_stats["start_time"] = None
    live_test_stats["inference_times"] = []
    
    return jsonify({"success": True, "message": "Statistics reset"})

@app.route('/capture_frame', methods=['POST'])
def capture_frame():
    """Capture current frame with bounding boxes"""
    global output_frame, lock
    
    try:
        import os
        from datetime import datetime
        
        # Get scenario name from request (optional)
        data = request.get_json() or {}
        scenario_name = data.get('scenario_name', 'capture')
        
        # Get current frame
        with lock:
            if output_frame is None:
                return jsonify({"success": False, "error": "No frame available"}), 503
            frame = output_frame.copy()
        
        # Draw bounding boxes on frame
        frame_with_boxes = draw_bounding_boxes(frame)
        
        # Create test_results directory if not exists
        results_dir = os.path.join(os.path.dirname(__file__), 'test_results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{scenario_name}_{timestamp}.jpg"
        filepath = os.path.join(results_dir, filename)
        
        # Save image with high quality
        cv2.imwrite(filepath, frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        logger.info(f"📸 Frame captured: {filename}")
        
        return jsonify({
            "success": True,
            "filename": filename,
            "path": filepath,
            "message": f"Image saved as {filename}"
        })
        
    except Exception as e:
        logger.error(f"Capture error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/download/bab4')
def download_bab4():
    """Download BAB IV DOCX file"""
    from flask import send_file
    import os
    
    file_path = os.path.join(os.path.dirname(__file__), 'BAB_IV_HASIL_DAN_PEMBAHASAN.docx')
    
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name='BAB_IV_HASIL_DAN_PEMBAHASAN.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    else:
        return jsonify({'error': 'File not found'}), 404


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚗 DROWSINESS DETECTION - SINGLE SERVER")
    print("="*60)
    
    
    # Display version info
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
        print("\n❌ Failed to initialize camera!")
        exit(1)
    
    if not initialize_model():
        print("\n⚠️ WARNING: Model failed to load!")
        print("   App will run but predictions will not work.")
        print("   Please fix model compatibility issue.")
        # Don't exit - allow app to run for testing interface
    
    if initialize_hardware():
        print("✅ Hardware alerts enabled")
    else:
        print("⚠️ Hardware alerts disabled")
    
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()
    
    print(f"\n✅ Camera Type: {camera_type}")
    print("✅ Model loaded")
    print("\n" + "="*60)
    print("🌐 Open in browser: http://192.168.18.150:5000")
    print("="*60 + "\n")
    
    def cleanup():
        global hardware, camera, camera_type, stop_capture_thread
        logger.info("Cleaning up...")
        
        # Signal capture thread to stop
        stop_capture_thread = True
        time.sleep(0.5)  # Give thread time to stop
        
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
    
    # Register cleanup for normal exit
    atexit.register(cleanup)
    
    # Handle Ctrl+C (SIGINT) and kill signals (SIGTERM)
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