#!/usr/bin/env python3
"""
Resource Monitor for Raspberry Pi
Monitors CPU, RAM, Temperature, and Power usage
"""

import psutil
import time
import subprocess

def get_cpu_temp():
    """Get CPU temperature on Raspberry Pi"""
    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
        return float(temp.replace("temp=", "").replace("'C\n", ""))
    except:
        return 0.0

def get_power_usage():
    """Estimate power usage (rough calculation)"""
    # Raspberry Pi 5 base power ~2.5W idle, up to 5W under load
    # This is an estimation based on CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    base_power = 2.5
    max_power = 5.0
    estimated_power = base_power + (max_power - base_power) * (cpu_percent / 100)
    return round(estimated_power, 1)

def get_resource_stats():
    """Get current resource statistics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    ram_gb = memory.used / (1024 ** 3)
    temp = get_cpu_temp()
    power = get_power_usage()
    
    return {
        "cpu_percent": round(cpu_percent, 1),
        "ram_gb": round(ram_gb, 2),
        "temp_c": round(temp, 1),
        "power_w": power
    }

if __name__ == "__main__":
    print("Resource Monitor - Raspberry Pi")
    print("=" * 50)
    
    while True:
        stats = get_resource_stats()
        print(f"\rCPU: {stats['cpu_percent']}% | RAM: {stats['ram_gb']}GB | Temp: {stats['temp_c']}°C | Power: {stats['power_w']}W", end="")
        time.sleep(2)
