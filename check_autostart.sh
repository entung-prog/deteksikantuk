#!/bin/bash
# Diagnostic script untuk troubleshooting autostart detection issue

echo "=========================================="
echo "🔍 Drowsiness Auto-Detection Diagnostic"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Service Status
echo "1️⃣  Service Status:"
echo "-------------------"
if sudo systemctl is-active --quiet drowsiness-auto; then
    echo -e "${GREEN}✅ Service is RUNNING${NC}"
else
    echo -e "${RED}❌ Service is NOT RUNNING${NC}"
    echo "   Try: sudo systemctl start drowsiness-auto"
fi
echo ""

# 2. Camera Detection
echo "2️⃣  Camera Detection:"
echo "-------------------"
if ls /dev/video* &> /dev/null; then
    echo -e "${GREEN}✅ Camera devices found:${NC}"
    ls -la /dev/video* 2>/dev/null
else
    echo -e "${RED}❌ No camera devices found${NC}"
    echo "   Check camera connection"
fi
echo ""

# 3. Model File
echo "3️⃣  Model File:"
echo "-------------------"
MODEL_PATH="$HOME/deteksikantuk/backend/best_model_compatible.tflite"
if [ -f "$MODEL_PATH" ]; then
    echo -e "${GREEN}✅ Model file exists${NC}"
    ls -lh "$MODEL_PATH"
else
    echo -e "${RED}❌ Model file NOT found${NC}"
    echo "   Expected: $MODEL_PATH"
fi
echo ""

# 4. Virtual Environment
echo "4️⃣  Virtual Environment:"
echo "-------------------"
VENV_PATH="$HOME/deteksikantuk/backend/venv"
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
    if [ -f "$VENV_PATH/bin/python3" ]; then
        echo "   Python: $($VENV_PATH/bin/python3 --version)"
    fi
else
    echo -e "${RED}❌ Virtual environment NOT found${NC}"
    echo "   Expected: $VENV_PATH"
fi
echo ""

# 5. Check Critical Log Messages
echo "5️⃣  Startup Log Analysis:"
echo "-------------------"
echo "Checking for critical initialization messages..."
echo ""

# Camera initialization
if sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Camera initialized"; then
    echo -e "${GREEN}✅ Camera initialized${NC}"
    sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep "Camera initialized" | tail -1
else
    echo -e "${RED}❌ Camera NOT initialized${NC}"
fi

# Model loading
if sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Model loaded"; then
    echo -e "${GREEN}✅ Model loaded${NC}"
    sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep "Model loaded" | tail -1
else
    echo -e "${RED}❌ Model NOT loaded${NC}"
fi

# Face cascade
if sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Face cascade loaded"; then
    echo -e "${GREEN}✅ Face cascade loaded${NC}"
    sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep "Face cascade loaded" | tail -1
else
    echo -e "${RED}❌ Face cascade NOT loaded${NC}"
fi

# Auto-detection thread
if sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Auto-detection enabled"; then
    echo -e "${GREEN}✅ Auto-detection enabled${NC}"
else
    echo -e "${RED}❌ Auto-detection NOT enabled${NC}"
fi

# Detection thread started
if sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Auto-detection thread started"; then
    echo -e "${GREEN}✅ Detection thread started${NC}"
else
    echo -e "${RED}❌ Detection thread NOT started${NC}"
fi

echo ""

# 6. Recent Errors
echo "6️⃣  Recent Errors:"
echo "-------------------"
ERROR_COUNT=$(sudo journalctl -u drowsiness-auto -n 100 --no-pager | grep -i "error\|failed\|exception" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No errors found in recent logs${NC}"
else
    echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error(s) in recent logs:${NC}"
    sudo journalctl -u drowsiness-auto -n 100 --no-pager | grep -i "error\|failed\|exception" | tail -5
fi
echo ""

# 7. Port Check
echo "7️⃣  Port Status:"
echo "-------------------"
if netstat -tuln 2>/dev/null | grep -q ":5000"; then
    echo -e "${GREEN}✅ Port 5000 is listening${NC}"
    IP_ADDR=$(hostname -I | awk '{print $1}')
    echo "   Web interface: http://$IP_ADDR:5000"
elif ss -tuln 2>/dev/null | grep -q ":5000"; then
    echo -e "${GREEN}✅ Port 5000 is listening${NC}"
    IP_ADDR=$(hostname -I | awk '{print $1}')
    echo "   Web interface: http://$IP_ADDR:5000"
else
    echo -e "${YELLOW}⚠️  Port 5000 not listening${NC}"
    echo "   Service may still be starting up"
fi
echo ""

# 8. Summary
echo "=========================================="
echo "📋 DIAGNOSTIC SUMMARY"
echo "=========================================="
echo ""

# Count issues
ISSUES=0

sudo systemctl is-active --quiet drowsiness-auto || ((ISSUES++))
ls /dev/video* &> /dev/null || ((ISSUES++))
[ -f "$MODEL_PATH" ] || ((ISSUES++))
[ -d "$VENV_PATH" ] || ((ISSUES++))
sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Camera initialized" || ((ISSUES++))
sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Model loaded" || ((ISSUES++))
sudo journalctl -u drowsiness-auto -n 200 --no-pager | grep -q "Auto-detection enabled" || ((ISSUES++))

if [ "$ISSUES" -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "If detection still not working:"
    echo "1. Check web interface statistics"
    echo "2. View live logs: sudo journalctl -u drowsiness-auto -f"
    echo "3. Check AUTOSTART_TROUBLESHOOTING.md for more details"
else
    echo -e "${RED}❌ Found $ISSUES issue(s)${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the errors above"
    echo "2. Check AUTOSTART_TROUBLESHOOTING.md for solutions"
    echo "3. View full logs: sudo journalctl -u drowsiness-auto -n 200"
fi

echo ""
echo "=========================================="
echo "For detailed troubleshooting, see:"
echo "  ~/deteksikantuk/AUTOSTART_TROUBLESHOOTING.md"
echo "=========================================="
