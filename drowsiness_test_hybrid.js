// ============================================================
// DROWSINESS DETECTION - HYBRID VERSION (Web UI + Python Backend)
// ============================================================

// Global Variables
let webcamStream = null;
let isVisualizationActive = false;
let isTestingActive = false;
let testingInterval = null;
let animationFrameId = null;

// Backend API URL
const API_URL = 'http://localhost:5000/api';

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

        // Check backend health
        modelStatus.textContent = 'Connecting to backend...';
        const healthCheck = await fetch(`${API_URL}/health`);
        const health = await healthCheck.json();

        if (health.status === 'ok' && health.model_loaded) {
            modelStatus.textContent = '✅ Ready';
            console.log('✅ Backend connected');
        } else {
            throw new Error('Backend not ready');
        }

        loadingOverlay.classList.add('hidden');

        // Setup webcam
        await setupWebcam();

        // Setup event listeners
        setupEventListeners();

        console.log('✅ Initialization complete');

    } catch (error) {
        console.error('Initialization error:', error);
        modelStatus.textContent = '❌ Backend Error';
        loadingOverlay.querySelector('.loading-text').textContent =
            'Cannot connect to backend. Make sure to run: python backend_server.py';
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

        await new Promise((resolve) => {
            webcam.onloadedmetadata = () => {
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
    btnVisualization.addEventListener('click', toggleVisualization);
    btnTesting.addEventListener('click', toggleTesting);
    btnExport.addEventListener('click', exportResults);
    btnClear.addEventListener('click', clearResults);

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

    if (!isVisualizationActive) {
        toggleVisualization();
    }

    const interval = parseInt(captureIntervalInput.value) * 1000;
    testingInterval = setInterval(captureTestResult, interval);
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

    if (result && result.faceDetected) {
        const timestamp = new Date().toLocaleTimeString('id-ID');
        const status = result.isDrowsy ? 'Drowsy' : 'Alert';
        const confidence = (result.confidence * 100).toFixed(1);
        const duration = currentDrowsyDuration.toFixed(1);

        testResults.push({
            timestamp,
            status,
            confidence: parseFloat(confidence),
            duration: parseFloat(duration)
        });

        updateResultsTable();
        updateSummary();
    }
}

// ============================================================
// DETECTION & PREDICTION
// ============================================================

async function detectAndPredict(visualize = true) {
    try {
        // Capture frame from webcam
        const canvas = document.createElement('canvas');
        canvas.width = webcam.videoWidth;
        canvas.height = webcam.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(webcam, 0, 0);

        // Convert to base64
        const imageData = canvas.toDataURL('image/jpeg', 0.8);

        // Send to backend
        const threshold = parseFloat(drowsyThresholdInput.value);
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData,
                threshold: threshold
            })
        });

        const result = await response.json();

        if (!result.face_detected) {
            updateStatus('NO FACE', null, false);
            resetDrowsyState();
            return { faceDetected: false };
        }

        if (result.confidence === null) {
            updateStatus('NO EYES', null, false);
            return { faceDetected: false };
        }

        // Draw face box if visualizing
        if (visualize && result.face_box) {
            const box = result.face_box;
            // Mirror the box
            const mirroredX = overlay.width - (box.x + box.width);
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.strokeRect(mirroredX, box.y, box.width, box.height);
        }

        // Update drowsy state
        updateDrowsyState(result.is_drowsy);

        // Update UI
        updateStatus(
            result.is_drowsy ? 'DROWSY' : 'ALERT',
            result.confidence,
            result.is_drowsy
        );

        return {
            faceDetected: true,
            isDrowsy: result.is_drowsy,
            confidence: result.confidence
        };

    } catch (error) {
        console.error('Detection error:', error);
        updateStatus('ERROR', null, false);
        return { faceDetected: false };
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
        drowsyDuration.textContent = currentDrowsyDuration.toFixed(1) + 's';

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

    if (status === 'NO FACE' || status === 'NO EYES' || status === 'ERROR') {
        statusText.className = 'status-text status-no-face';
    } else if (isDrowsy) {
        statusText.className = 'status-text status-drowsy';
    } else {
        statusText.className = 'status-text status-alert';
    }
}

// ============================================================
// RESULTS TABLE
// ============================================================

function updateResultsTable() {
    resultsBody.innerHTML = '';

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

    let csv = 'No,Timestamp,Status,Confidence (%),Duration (s)\n';
    testResults.forEach((result, index) => {
        csv += `${index + 1},${result.timestamp},${result.status},${result.confidence},${result.duration}\n`;
    });

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
