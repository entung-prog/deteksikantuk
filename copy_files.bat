@echo off
REM Batch script to copy files to Raspberry Pi
REM Usage: copy_files.bat

echo ==========================================
echo Copying files to Raspberry Pi
echo ==========================================
echo.
echo Target: entung@192.168.0.108
echo Directory: ~/drowsiness-detection
echo.
echo You will be asked for password multiple times
echo.

REM Create directory first
echo [1/8] Creating directory...
ssh entung@192.168.0.108 "mkdir -p ~/drowsiness-detection"

REM Copy application files
echo.
echo [2/8] Copying backend_server.py...
scp backend_server.py entung@192.168.0.108:~/drowsiness-detection/

echo.
echo [3/8] Copying drowsiness_test.html...
scp drowsiness_test.html entung@192.168.0.108:~/drowsiness-detection/

echo.
echo [4/8] Copying drowsiness_test.css...
scp drowsiness_test.css entung@192.168.0.108:~/drowsiness-detection/

echo.
echo [5/8] Copying drowsiness_test_hybrid.js...
scp drowsiness_test_hybrid.js entung@192.168.0.108:~/drowsiness-detection/

echo.
echo [6/8] Copying requirements.txt...
scp requirements.txt entung@192.168.0.108:~/drowsiness-detection/

echo.
echo [7/8] Copying deploy.sh...
scp deploy.sh entung@192.168.0.108:~/drowsiness-detection/

echo.
echo [8/8] Copying best_model.h5...
scp ..\best_model.h5 entung@192.168.0.108:~/drowsiness-detection/

echo.
echo ==========================================
echo Transfer Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. SSH to Raspberry Pi:
echo    ssh entung@192.168.0.108
echo.
echo 2. Run deployment:
echo    cd ~/drowsiness-detection
echo    chmod +x deploy.sh
echo    ./deploy.sh
echo.
pause
