#!/bin/bash

# Script untuk sinkronisasi file dari local ke Raspberry Pi menggunakan rsync
# Lebih efisien karena hanya copy file yang berubah

# Konfigurasi Raspberry Pi
RASPI_USER="pi"  # Ganti dengan username Raspberry Pi Anda
RASPI_IP="192.168.18.150"  # Ganti dengan IP Raspberry Pi Anda
RASPI_PATH="~/deteksikantuk"  # Path di Raspberry Pi

# Warna untuk output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Sync Project ke Raspberry Pi${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Cek koneksi ke Raspberry Pi
echo -e "${YELLOW}Mengecek koneksi ke Raspberry Pi...${NC}"
if ping -c 1 $RASPI_IP &> /dev/null; then
    echo -e "${GREEN}✓ Raspberry Pi dapat dijangkau${NC}"
else
    echo -e "${RED}✗ Tidak dapat terhubung ke Raspberry Pi${NC}"
    echo "Pastikan Raspberry Pi sudah menyala dan terhubung ke jaringan"
    exit 1
fi

echo ""
echo -e "${YELLOW}Membuat direktori di Raspberry Pi...${NC}"
ssh ${RASPI_USER}@${RASPI_IP} "mkdir -p ${RASPI_PATH}"

echo ""
echo -e "${YELLOW}Sinkronisasi file...${NC}"

# Rsync dengan opsi:
# -a: archive mode (preserve permissions, timestamps, etc)
# -v: verbose
# -z: compress during transfer
# --progress: show progress
# --exclude: exclude files/folders

rsync -avz --progress \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude '.git/' \
  --exclude '*.pyc' \
  --exclude '.lgd-nfy0' \
  backend/ README.md \
  ${RASPI_USER}@${RASPI_IP}:${RASPI_PATH}/

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Sinkronisasi selesai!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}File yang di-sync:${NC}"
echo "  • backend/app.py"
echo "  • backend/best_model.tflite"
echo "  • backend/requirements.txt"
echo "  • README.md"
echo ""
echo -e "${BLUE}Langkah selanjutnya di Raspberry Pi:${NC}"
echo ""
echo "1. SSH ke Raspberry Pi:"
echo "   ssh ${RASPI_USER}@${RASPI_IP}"
echo ""
echo "2. Masuk ke direktori project:"
echo "   cd ${RASPI_PATH}/backend"
echo ""
echo "3. Buat virtual environment (jika belum):"
echo "   python3 -m venv ../venv"
echo ""
echo "4. Aktifkan virtual environment:"
echo "   source ../venv/bin/activate"
echo ""
echo "5. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "6. Jalankan aplikasi:"
echo "   python3 app.py"
echo ""
