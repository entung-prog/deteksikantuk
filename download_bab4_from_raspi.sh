#!/bin/bash
# Script untuk download BAB IV dari Raspberry Pi ke laptop lokal

echo "🔍 Mencari Raspberry Pi di jaringan..."

# Coba beberapa kemungkinan IP Raspberry Pi
RASPI_IPS=(
    "192.168.42.129"
    "192.168.1.100"
    "raspberrypi.local"
)

RASPI_USER="entung"
SOURCE_FILE="/home/entung/deteksikantuk/backend/BAB_IV_HASIL_DAN_PEMBAHASAN.docx"
DEST_DIR="$HOME/Downloads"

# Coba setiap IP
for RASPI_IP in "${RASPI_IPS[@]}"; do
    echo "Mencoba koneksi ke $RASPI_IP..."
    
    if ping -c 1 -W 2 "$RASPI_IP" &> /dev/null; then
        echo "✓ Raspberry Pi ditemukan di $RASPI_IP"
        echo ""
        echo "📥 Mendownload file BAB IV..."
        
        # Download menggunakan scp
        scp "${RASPI_USER}@${RASPI_IP}:${SOURCE_FILE}" "${DEST_DIR}/"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ File berhasil didownload!"
            echo "📄 Lokasi: ${DEST_DIR}/BAB_IV_HASIL_DAN_PEMBAHASAN.docx"
            ls -lh "${DEST_DIR}/BAB_IV_HASIL_DAN_PEMBAHASAN.docx"
            exit 0
        else
            echo "❌ Gagal download dari $RASPI_IP"
        fi
    fi
done

echo ""
echo "❌ Tidak dapat menemukan Raspberry Pi di jaringan"
echo ""
echo "Alternatif manual:"
echo "1. Pastikan Raspberry Pi terhubung ke jaringan yang sama"
echo "2. Jalankan command berikut secara manual:"
echo ""
echo "   scp entung@<IP_RASPI>:/home/entung/deteksikantuk/backend/BAB_IV_HASIL_DAN_PEMBAHASAN.docx ~/Downloads/"
echo ""
echo "   Ganti <IP_RASPI> dengan IP Raspberry Pi Anda"
