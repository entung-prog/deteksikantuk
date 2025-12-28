#!/usr/bin/env python3
"""
Script untuk Generate Analisis Hasil Pengujian
Membaca semua CSV di folder test_results dan membuat analisis lengkap
"""

import os
import csv
from datetime import datetime
from pathlib import Path

def parse_csv(filepath):
    """Parse CSV file dan extract data penting"""
    data = {
        'scenario': '',
        'timestamp': '',
        'duration': 0,
        'total_detections': 0,
        'drowsy_detected': 0,
        'alert_detected': 0,
        'avg_inference': 0,
        'cpu_percent': 0,
        'ram_gb': 0,
        'inference_times': []
    }
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
        # Parse header metadata
        for line in lines[:10]:
            if line.startswith('# Scenario,'):
                data['scenario'] = line.split(',')[1].strip()
            elif line.startswith('# Timestamp,'):
                data['timestamp'] = line.split(',', 1)[1].strip()
            elif line.startswith('# Duration,'):
                duration_str = line.split(',')[1].strip()
                # Extract number from "33.3 seconds"
                data['duration'] = float(duration_str.split()[0])
        
        # Parse summary statistics
        in_summary = False
        in_resource = False
        in_inference = False
        
        for line in lines:
            line = line.strip()
            
            if line == 'Summary Statistics':
                in_summary = True
                continue
            elif line == 'Resource Usage':
                in_summary = False
                in_resource = True
                continue
            elif line.startswith('Inference Times'):
                in_resource = False
                in_inference = True
                continue
            
            if in_summary and ',' in line and not line.startswith('Metric'):
                parts = line.split(',')
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    if key == 'Total Detections':
                        data['total_detections'] = int(value)
                    elif key == 'Drowsy Detected':
                        data['drowsy_detected'] = int(value)
                    elif key == 'Alert Detected':
                        data['alert_detected'] = int(value)
                    elif key == 'Avg Inference Time (ms)':
                        data['avg_inference'] = float(value)
            
            if in_resource and ',' in line and not line.startswith('Resource'):
                parts = line.split(',')
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    if key == 'CPU Usage (%)':
                        data['cpu_percent'] = float(value)
                    elif key == 'RAM Usage (GB)':
                        data['ram_gb'] = float(value)
            
            if in_inference and ',' in line and not line.startswith('Sample'):
                parts = line.split(',')
                if len(parts) == 2:
                    try:
                        time_ms = float(parts[1].strip())
                        data['inference_times'].append(time_ms)
                    except:
                        pass
    
    return data

def calculate_fps(avg_inference_ms):
    """Calculate FPS from average inference time"""
    if avg_inference_ms > 0:
        return 1000.0 / avg_inference_ms
    return 0

def generate_analysis(test_results_dir):
    """Generate comprehensive analysis from all CSV files"""
    
    # Find all CSV files
    csv_files = list(Path(test_results_dir).glob('*.csv'))
    
    if not csv_files:
        print("❌ No CSV files found in test_results/")
        return
    
    print(f"📊 Found {len(csv_files)} CSV files")
    
    # Parse all CSV files
    all_data = []
    for csv_file in csv_files:
        print(f"   Reading: {csv_file.name}")
        data = parse_csv(csv_file)
        all_data.append(data)
    
    # Sort by scenario name
    all_data.sort(key=lambda x: x['scenario'])
    
    # Generate markdown report
    output_file = os.path.join(test_results_dir, 'ANALISIS_HASIL.md')
    
    with open(output_file, 'w') as f:
        # Header
        f.write("# 📊 ANALISIS HASIL PENGUJIAN SISTEM DETEKSI KANTUK\n")
        f.write(f"**Tanggal**: {datetime.now().strftime('%d %B %Y')}\n")
        f.write(f"**Waktu Generate**: {datetime.now().strftime('%H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Summary Table
        f.write("## 📋 RINGKASAN SEMUA SKENARIO\n\n")
        f.write("| Skenario | Durasi | Total Samples | Drowsy | Alert | Avg Inference (ms) | FPS | CPU (%) | RAM (GB) |\n")
        f.write("|----------|--------|---------------|--------|-------|-------------------|-----|---------|----------|\n")
        
        for data in all_data:
            fps = calculate_fps(data['avg_inference'])
            scenario_name = data['scenario'].replace('_', ' ').title()
            f.write(f"| **{scenario_name}** | {data['duration']:.1f}s | {data['total_detections']} | "
                   f"{data['drowsy_detected']} | {data['alert_detected']} | {data['avg_inference']:.2f} | "
                   f"{fps:.1f} | {data['cpu_percent']:.1f} | {data['ram_gb']:.2f} |\n")
        
        f.write("\n---\n\n")
        
        # Detailed Analysis per Scenario
        f.write("## 🎯 ANALISIS PER SKENARIO\n\n")
        
        for idx, data in enumerate(all_data, 1):
            scenario_name = data['scenario'].replace('_', ' ').title()
            total = data['total_detections']
            drowsy = data['drowsy_detected']
            alert = data['alert_detected']
            
            drowsy_pct = (drowsy / total * 100) if total > 0 else 0
            alert_pct = (alert / total * 100) if total > 0 else 0
            fps = calculate_fps(data['avg_inference'])
            
            f.write(f"### {idx}. {scenario_name}\n")
            f.write(f"**Hasil**:\n")
            f.write(f"- Total Detections: {total} samples\n")
            f.write(f"- Drowsy: {drowsy} ({drowsy_pct:.1f}%)\n")
            f.write(f"- Alert: {alert} ({alert_pct:.1f}%)\n")
            f.write(f"- Avg Inference: {data['avg_inference']:.2f} ms (~{fps:.1f} FPS)\n")
            f.write(f"- CPU: {data['cpu_percent']:.1f}%\n")
            f.write(f"- RAM: {data['ram_gb']:.2f} GB\n\n")
            
            # Analysis based on scenario type
            f.write(f"**Analisis**:\n")
            
            if 'normal' in data['scenario'].lower():
                if alert_pct > 80:
                    f.write(f"- ✅ **BAIK**: {alert_pct:.1f}% terdeteksi sebagai Alert (tidak kantuk)\n")
                else:
                    f.write(f"- ⚠️ **PERHATIAN**: Hanya {alert_pct:.1f}% terdeteksi Alert\n")
                if drowsy_pct > 20:
                    f.write(f"- ⚠️ **False Positive**: {drowsy_pct:.1f}% salah deteksi kantuk\n")
            
            elif 'drowsiness' in data['scenario'].lower():
                if drowsy_pct > 70:
                    f.write(f"- ✅ **BAIK**: {drowsy_pct:.1f}% terdeteksi kantuk\n")
                elif drowsy_pct > 40:
                    f.write(f"- ⚠️ **CUKUP**: {drowsy_pct:.1f}% terdeteksi kantuk\n")
                else:
                    f.write(f"- ❌ **KURANG**: Hanya {drowsy_pct:.1f}% terdeteksi kantuk\n")
                    f.write(f"- **False Negative tinggi**: {alert_pct:.1f}% miss detection\n")
            
            elif 'blinking' in data['scenario'].lower():
                if alert_pct > 90:
                    f.write(f"- ✅ **SANGAT BAIK**: {alert_pct:.1f}% kedipan tidak dianggap kantuk\n")
                elif alert_pct > 70:
                    f.write(f"- ⚠️ **CUKUP**: {alert_pct:.1f}% kedipan benar\n")
                else:
                    f.write(f"- ❌ **BURUK**: {drowsy_pct:.1f}% kedipan salah dianggap kantuk\n")
            
            elif 'light' in data['scenario'].lower():
                if 'low' in data['scenario'].lower():
                    if drowsy_pct > 60:
                        f.write(f"- ⚠️ **OVER-DETECTION**: {drowsy_pct:.1f}% terdeteksi kantuk (terlalu sensitif)\n")
                    else:
                        f.write(f"- ✅ **BAIK**: Deteksi seimbang di low light\n")
                else:  # bright light
                    if alert_pct > 90:
                        f.write(f"- ✅ **SANGAT BAIK**: {alert_pct:.1f}% akurasi di pencahayaan tinggi\n")
                    else:
                        f.write(f"- ⚠️ **CUKUP**: {alert_pct:.1f}% akurasi\n")
            
            f.write("\n---\n\n")
        
        # Performance Analysis
        f.write("## 📈 PERFORMA SISTEM\n\n")
        f.write("### Inference Time & FPS\n")
        f.write("| Skenario | Avg Inference (ms) | Est. FPS | Keterangan |\n")
        f.write("|----------|-------------------|----------|------------|\n")
        
        # Sort by inference time
        sorted_by_inference = sorted(all_data, key=lambda x: x['avg_inference'])
        for data in sorted_by_inference:
            scenario_name = data['scenario'].replace('_', ' ').title()
            fps = calculate_fps(data['avg_inference'])
            
            if fps > 8:
                status = "Sangat Baik"
            elif fps > 6:
                status = "Baik"
            elif fps > 4:
                status = "Cukup"
            else:
                status = "Perlu Optimasi"
            
            f.write(f"| {scenario_name} | {data['avg_inference']:.2f} | ~{fps:.1f} | {status} |\n")
        
        f.write("\n")
        
        # Resource Usage
        f.write("### Resource Usage\n")
        cpu_values = [d['cpu_percent'] for d in all_data]
        ram_values = [d['ram_gb'] for d in all_data]
        
        f.write("| Resource | Min | Max | Avg | Keterangan |\n")
        f.write("|----------|-----|-----|-----|------------|\n")
        f.write(f"| CPU | {min(cpu_values):.1f}% | {max(cpu_values):.1f}% | "
               f"{sum(cpu_values)/len(cpu_values):.1f}% | Bervariasi tergantung load |\n")
        f.write(f"| RAM | {min(ram_values):.2f} GB | {max(ram_values):.2f} GB | "
               f"{sum(ram_values)/len(ram_values):.2f} GB | Stabil |\n")
        
        f.write("\n---\n\n")
        
        # Conclusions
        f.write("## 🎯 KESIMPULAN\n\n")
        
        # Find best and worst scenarios
        best_scenario = max(all_data, key=lambda x: x['alert_detected'] / max(x['total_detections'], 1))
        worst_scenario = min(all_data, key=lambda x: x['alert_detected'] / max(x['total_detections'], 1))
        
        f.write("### Kekuatan Sistem:\n")
        best_name = best_scenario['scenario'].replace('_', ' ').title()
        best_acc = (best_scenario['alert_detected'] / max(best_scenario['total_detections'], 1)) * 100
        f.write(f"1. ✅ **{best_name}**: Akurasi {best_acc:.1f}% - sangat baik\n")
        
        avg_fps = sum([calculate_fps(d['avg_inference']) for d in all_data]) / len(all_data)
        f.write(f"2. ✅ **Performance**: FPS rata-rata {avg_fps:.1f} - ")
        if avg_fps > 6:
            f.write("baik untuk real-time detection\n")
        else:
            f.write("cukup untuk detection\n")
        
        avg_ram = sum(ram_values) / len(ram_values)
        f.write(f"3. ✅ **Resource**: RAM stabil ~{avg_ram:.2f} GB\n\n")
        
        f.write("### Kelemahan Sistem:\n")
        worst_name = worst_scenario['scenario'].replace('_', ' ').title()
        worst_acc = (worst_scenario['alert_detected'] / max(worst_scenario['total_detections'], 1)) * 100
        f.write(f"1. ❌ **{worst_name}**: Akurasi {worst_acc:.1f}% - perlu perbaikan\n")
        
        if avg_fps < 10:
            f.write(f"2. ⚠️ **FPS**: {avg_fps:.1f} FPS - bisa ditingkatkan ke 10+ FPS\n")
        
        f.write("\n### Rekomendasi Perbaikan:\n")
        f.write("1. **Tuning Threshold**: Sesuaikan confidence threshold untuk mengurangi false positive/negative\n")
        f.write("2. **Model Improvement**: Retrain dengan lebih banyak data untuk skenario yang lemah\n")
        f.write("3. **Preprocessing**: Tambahkan brightness normalization untuk kondisi lighting bervariasi\n")
        f.write("4. **Temporal Analysis**: Implementasi tracking durasi untuk membedakan kedipan vs kantuk\n")
        
        f.write("\n---\n\n")
        f.write(f"**Dibuat oleh**: Script Analisis Otomatis\n")
        f.write(f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"\n✅ Analisis berhasil dibuat: {output_file}")
    print(f"📊 Total {len(all_data)} skenario dianalisis")

if __name__ == '__main__':
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_results_dir = os.path.join(script_dir, 'test_results')
    
    if not os.path.exists(test_results_dir):
        print(f"❌ Folder test_results tidak ditemukan: {test_results_dir}")
        exit(1)
    
    print("=" * 60)
    print("📊 GENERATE ANALISIS HASIL PENGUJIAN")
    print("=" * 60)
    print()
    
    generate_analysis(test_results_dir)
    
    print()
    print("=" * 60)
    print("✅ SELESAI!")
    print("=" * 60)
