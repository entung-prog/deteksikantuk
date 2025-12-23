// ============================================================
// DROWSINESS DETECTION - JAVASCRIPT
// ============================================================

// Global Variables
let model = null;
let faceDetector = null;
let webcamStream = null;
let isVisualizationActive = false;
let isTestingActive = false;
let testingInterval = null;
let animationFrameId = null;

// DOM Elements
const webcam = document.getElementById('webcam');
const overlay = document.getElementById('overlay');
const ctx = overlay.getContext('2d');
const loadingOverlay = document.getElementById('loading-overlay');

// Buttons
const btnVisualization = document.getElementById('btn-visualization');
const btnTesting = document.getElementById('btn-testing');
const btnExport = document.getElementById('btn-export');
const btnClear = document.getElementById('btn-clear');

// Status Elements
const statusText = document.getElementById('status-text');
const confidenceText = document.getElementById('confidence-text');
const fpsCounter = document.getElementById('fps-counter');
const modelStatus = document.getElementById('model-status');
const drowsyDuration = document.getElementById('drowsy-duration');
const totalTests = document.getElementById('total-tests');
const alarmOverlay = document.getElementById('alarm-overlay');

// Settings
const drowsyThresholdInput = document.getElementById('drowsy-threshold');
const thresholdValue = document.getElementById('threshold-value');
const alarmDurationInput = document.getElementById('alarm-duration');
const captureIntervalInput = document.getElementById('capture-interval');

// Results
const resultsBody = document.getElementById('results-body');
const alertCount = document.getElementById('alert-count');
const drowsyCount = document.getElementById('drowsy-count');
const avgConfidence = document.getElementById('avg-confidence');

// State
let testResults = [];
let drowsyFrameCount = 0;
let drowsyStartTime = null;
let currentDrowsyDuration = 0;
let lastFrameTime = Date.now();
let fps = 0;

// ============================================================
// INITIALIZATION
// ============================================================

async function init() {
    try {
        console.log('Initializing...');
        
        // Load TensorFlow.js model
        modelStatus.textContent = 'Loading model...';
        model = await tf.loadGraphModel('./model_tfjs/model.json');
        console.log('✅ Model loaded');
        
        // Load face detector
        modelStatus.textContent = 'Loading face detector...';
        faceDetector = await blazeface.load();
        console.log('✅ Face detector loaded');
        
        modelStatus.textContent = '✅ Ready';
        loadingOverlay.classList.add('hidden');
        
        // Setup webcam
        await setupWebcam();
        
        // Setup event listeners
        setupEventListeners();
        
        console.log('✅ Initialization complete');
        
    } catch (error) {
        console.error('Initialization error:', error);
        modelStatus.textContent = '❌ Error';
        loadingOverlay.querySelector('.loading-text').textContent = 
            'Error loading models. Make sure model files are in ./model_tfjs/ folder.';
    }
}

// ============================================================
// WEBCAM SETUP
// ============================================================

async function setupWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 }
        });
        webcam.srcObject = webcamStream;
        
        // Wait for video to be ready
        await new Promise((resolve) => {
            webcam.onloadedmetadata = () => {
                // Set canvas size to match video
                overlay.width = webcam.videoWidth;
                overlay.height = webcam.videoHeight;
                resolve();
            };
        });
        
        console.log('✅ Webcam ready');
    } catch (error) {
        console.error('Webcam error:', error);
        alert('Cannot access webcam. Please grant camera permission.');
    }
}

// ============================================================
// EVENT LISTENERS
// ============================================================

function setupEventListeners() {
    // Visualization button
    btnVisualization.addEventListener('click', toggleVisualization);
    
    // Testing button
    btnTesting.addEventListener('click', toggleTesting);
    
    // Export button
    btnExport.addEventListener('click', exportResults);
    
    // Clear button
    btnClear.addEventListener('click', clearResults);
    
    // Threshold slider
    drowsyThresholdInput.addEventListener('input', (e) => {
        thresholdValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
}

// ============================================================
// VISUALIZATION MODE
// ============================================================

function toggleVisualization() {
    isVisualizationActive = !isVisualizationActive;
    
    if (isVisualizationActive) {
        btnVisualization.textContent = '⏸️ Stop Visualization';
        btnVisualization.classList.add('active');
        startVisualization();
    } else {
        btnVisualization.textContent = '👁️ Start Visualization';
        btnVisualization.classList.remove('active');
        stopVisualization();
    }
}

function startVisualization() {
    console.log('Starting visualization...');
    visualizationLoop();
}

function stopVisualization() {
    console.log('Stopping visualization...');
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
    // Clear canvas
    ctx.clearRect(0, 0, overlay.width, overlay.height);
}

async function visualizationLoop() {
    if (!isVisualizationActive) return;
    
    // Calculate FPS
    const now = Date.now();
    const delta = now - lastFrameTime;
    fps = Math.round(1000 / delta);
    lastFrameTime = now;
    fpsCounter.textContent = `FPS: ${fps}`;
    
    // Clear canvas
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    
    // Detect and predict
    await detectAndPredict();
    
    // Continue loop
    animationFrameId = requestAnimationFrame(visualizationLoop);
}

// ============================================================
// TESTING MODE
// ============================================================

function toggleTesting() {
    isTestingActive = !isTestingActive;
    
    if (isTestingActive) {
        btnTesting.textContent = '⏹️ Stop Testing';
        btnTesting.classList.add('active');
        startTesting();
    } else {
        btnTesting.textContent = '📊 Start Testing Mode';
        btnTesting.classList.remove('active');
        stopTesting();
    }
}

function startTesting() {
    console.log('Starting testing mode...');
    
    // Also start visualization
    if (!isVisualizationActive) {
        toggleVisualization();
    }
    
    // Start periodic capture
    const interval = parseInt(captureIntervalInput.value) * 1000;
    testingInterval = setInterval(captureTestResult, interval);
    
    // Capture first result immediately
    captureTestResult();
}

function stopTesting() {
    console.log('Stopping testing mode...');
    if (testingInterval) {
        clearInterval(testingInterval);
        testingInterval = null;
    }
}

async function captureTestResult() {
    const result = await detectAndPredict(false);
    
    if (result) {
        const timestamp = new Date().toLocaleTimeString('id-ID');
        const status = result.isDrowsy ? 'Drowsy' : 'Alert';
        const confidence = (result.confidence * 100).toFixed(1);
        const duration = currentDrowsyDuration.toFixed(1);
        
        // Add to results array
        testResults.push({
            timestamp,
            status,
            confidence: parseFloat(confidence),
            duration: parseFloat(duration)
        });
        
        // Update table
        updateResultsTable();
        
        // Update summary
        updateSummary();
    }
}

// ============================================================
// FACE DETECTION & PREDICTION
// ============================================================

async function detectAndPredict(visualize = true) {
    try {
        // Detect faces
        const predictions = await faceDetector.estimateFaces(webcam, false);
        
        if (predictions.length === 0) {
            // No face detected
            updateStatus('NO FACE', null, false);
            resetDrowsyState();
            return null;
        }
        
        // Get first face
        const face = predictions[0];
        
        // Draw face box (mirrored)
        if (visualize) {
            drawMirroredBox(face.topLeft, face.bottomRight, '#3b82f6', 2);
        }
        
        // Extract eye regions
        const eyeRegions = extractEyeRegions(face);
        
        if (!eyeRegions) {
            updateStatus('NO EYES', null, false);
            return null;
        }
        
        // Draw eye boxes
        if (visualize) {
            drawMirroredBox(eyeRegions.leftEye.topLeft, eyeRegions.leftEye.bottomRight, '#10b981', 2);
            drawMirroredBox(eyeRegions.rightEye.topLeft, eyeRegions.rightEye.bottomRight, '#10b981', 2);
        }
        
        // Predict drowsiness
        const leftPred = await predictEyeRegion(eyeRegions.leftEye);
        const rightPred = await predictEyeRegion(eyeRegions.rightEye);
        
        // Average prediction
        const avgPred = (leftPred + rightPred) / 2;
        
        // Determine status
        const threshold = parseFloat(drowsyThresholdInput.value);
        const isDrowsy = avgPred < threshold;
        
        // Update drowsy state
        updateDrowsyState(isDrowsy);
        
        // Update UI
        updateStatus(isDrowsy ? 'DROWSY' : 'ALERT', avgPred, isDrowsy);
        
        return {
            isDrowsy,
            confidence: avgPred
        };
        
    } catch (error) {
        console.error('Detection error:', error);
        return null;
    }
}

function extractEyeRegions(face) {
    const [x1, y1] = face.topLeft;
    const [x2, y2] = face.bottomRight;
    const width = x2 - x1;
    const height = y2 - y1;
    
    // Eye region is in upper 40% of face
    const eyeY1 = y1 + height * 0.15;
    const eyeY2 = y1 + height * 0.45;
    
    // Left eye (right side of mirrored image)
    const leftX1 = x1 + width * 0.55;
    const leftX2 = x1 + width * 0.95;
    
    // Right eye (left side of mirrored image)
    const rightX1 = x1 + width * 0.05;
    const rightX2 = x1 + width * 0.45;
    
    return {
        leftEye: {
            topLeft: [leftX1, eyeY1],
            bottomRight: [leftX2, eyeY2]
        },
        rightEye: {
            topLeft: [rightX1, eyeY1],
            bottomRight: [rightX2, eyeY2]
        }
    };
}

async function predictEyeRegion(eyeBox) {
    try {
        // Create tensor from video at eye region
        const [x1, y1] = eyeBox.topLeft;
        const [x2, y2] = eyeBox.bottomRight;
        const width = x2 - x1;
        const height = y2 - y1;
        
        // Capture eye region from video
        const eyeTensor = tf.tidy(() => {
            // Capture from video
            const videoTensor = tf.browser.fromPixels(webcam);
            
            // Crop eye region
            const cropped = tf.image.cropAndResize(
                videoTensor.expandDims(0),
                [[y1 / webcam.videoHeight, x1 / webcam.videoWidth, 
                  y2 / webcam.videoHeight, x2 / webcam.videoWidth]],
                [0],
                [224, 224]
            );
            
            // Normalize to [0, 1]
            return cropped.div(255.0);
        });
        
        // Predict
        const prediction = await model.predict(eyeTensor);
        const value = await prediction.data();
        
        // Cleanup
        eyeTensor.dispose();
        prediction.dispose();
        
        return value[0];
        
    } catch (error) {
        console.error('Prediction error:', error);
        return 0.5; // Default neutral value
    }
}

// ============================================================
// DROWSY STATE MANAGEMENT
// ============================================================

function updateDrowsyState(isDrowsy) {
    if (isDrowsy) {
        if (drowsyStartTime === null) {
            drowsyStartTime = Date.now();
        }
        currentDrowsyDuration = (Date.now() - drowsyStartTime) / 1000;
        drowsyFrameCount++;
        
        // Update display
        drowsyDuration.textContent = currentDrowsyDuration.toFixed(1) + 's';
        
        // Check alarm
        const alarmDuration = parseFloat(alarmDurationInput.value);
        if (currentDrowsyDuration >= alarmDuration) {
            alarmOverlay.classList.remove('hidden');
        }
    } else {
        resetDrowsyState();
    }
}

function resetDrowsyState() {
    drowsyStartTime = null;
    currentDrowsyDuration = 0;
    drowsyFrameCount = 0;
    drowsyDuration.textContent = '0.0s';
    alarmOverlay.classList.add('hidden');
}

// ============================================================
// UI UPDATES
// ============================================================

function updateStatus(status, confidence, isDrowsy) {
    statusText.textContent = status;
    
    if (confidence !== null) {
        confidenceText.textContent = `Confidence: ${(confidence * 100).toFixed(1)}%`;
    } else {
        confidenceText.textContent = '--';
    }
    
    // Update colors
    const overlay = document.getElementById('status-overlay');
    if (status === 'NO FACE' || status === 'NO EYES') {
        statusText.className = 'status-text status-no-face';
    } else if (isDrowsy) {
        statusText.className = 'status-text status-drowsy';
    } else {
        statusText.className = 'status-text status-alert';
    }
}

function drawMirroredBox(topLeft, bottomRight, color, lineWidth) {
    const [x1, y1] = topLeft;
    const [x2, y2] = bottomRight;
    
    // Mirror x coordinates
    const mirroredX1 = overlay.width - x2;
    const mirroredX2 = overlay.width - x1;
    
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.strokeRect(mirroredX1, y1, mirroredX2 - mirroredX1, y2 - y1);
}

// ============================================================
// RESULTS TABLE
// ============================================================

function updateResultsTable() {
    // Clear table
    resultsBody.innerHTML = '';
    
    // Add rows (newest first)
    const reversedResults = [...testResults].reverse();
    reversedResults.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${testResults.length - index}</td>
            <td>${result.timestamp}</td>
            <td><span class="status-badge ${result.status.toLowerCase()}">${result.status}</span></td>
            <td>${result.confidence}%</td>
            <td>${result.duration}s</td>
        `;
        resultsBody.appendChild(row);
    });
    
    // Update total tests
    totalTests.textContent = testResults.length;
}

function updateSummary() {
    const alerts = testResults.filter(r => r.status === 'Alert').length;
    const drowsies = testResults.filter(r => r.status === 'Drowsy').length;
    const avgConf = testResults.length > 0
        ? (testResults.reduce((sum, r) => sum + r.confidence, 0) / testResults.length).toFixed(1)
        : '--';
    
    alertCount.textContent = alerts;
    drowsyCount.textContent = drowsies;
    avgConfidence.textContent = avgConf + (avgConf !== '--' ? '%' : '');
}

function clearResults() {
    if (confirm('Clear all test results?')) {
        testResults = [];
        resultsBody.innerHTML = '<tr class="no-data"><td colspan="5">No test data yet. Start testing mode to begin.</td></tr>';
        alertCount.textContent = '0';
        drowsyCount.textContent = '0';
        avgConfidence.textContent = '--';
        totalTests.textContent = '0';
    }
}

function exportResults() {
    if (testResults.length === 0) {
        alert('No test data to export!');
        return;
    }
    
    // Create CSV
    let csv = 'No,Timestamp,Status,Confidence (%),Duration (s)\n';
    testResults.forEach((result, index) => {
        csv += `${index + 1},${result.timestamp},${result.status},${result.confidence},${result.duration}\n`;
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `drowsiness_test_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('✅ Results exported');
}

// ============================================================
// START APPLICATION
// ============================================================

window.addEventListener('load', init);
