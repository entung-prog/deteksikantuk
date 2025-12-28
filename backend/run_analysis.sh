#!/bin/bash
# Script untuk generate analisis dan menampilkan summary

echo "============================================================"
echo "📊 GENERATE ANALISIS HASIL PENGUJIAN"
echo "============================================================"
echo ""

# Run Python script
python3 generate_analysis.py

echo ""
echo "============================================================"
echo "📋 QUICK SUMMARY"
echo "============================================================"
echo ""

# Count CSV files
csv_count=$(ls -1 test_results/*.csv 2>/dev/null | wc -l)
echo "Total CSV files: $csv_count"

# Show file sizes
echo ""
echo "File sizes:"
ls -lh test_results/*.csv 2>/dev/null | awk '{print "  " $9 " - " $5}'

# Show analysis file
echo ""
if [ -f "test_results/ANALISIS_HASIL.md" ]; then
    echo "✅ Analisis file created:"
    echo "  test_results/ANALISIS_HASIL.md"
    echo ""
    echo "Preview (first 30 lines):"
    echo "---"
    head -30 test_results/ANALISIS_HASIL.md
    echo "---"
    echo ""
    echo "📖 Buka file lengkap: test_results/ANALISIS_HASIL.md"
else
    echo "❌ Analisis file not found"
fi

echo ""
echo "============================================================"
