"""
Hardware Alert System - GPIO Control for Buzzer and RGB LED
============================================================
Controls buzzer and RGB LED based on drowsiness detection status
"""

import RPi.GPIO as GPIO
import time
import threading

class HardwareAlert:
    """
    Hardware alert system with buzzer and RGB LED
    
    Alert Levels:
    - GREEN (Alert): Confidence > 0.7 - Driver is alert
    - YELLOW (Warning): 0.4 < Confidence <= 0.7 - Drowsiness warning
    - RED (Drowsy): Confidence <= 0.4 - Drowsy detected, buzzer active
    """
    
    def __init__(self, buzzer_pin=17, led_red=22, led_green=27, led_blue=24):
        """
        Initialize GPIO pins
        
        Args:
            buzzer_pin: GPIO pin for buzzer (default: GPIO17)
            led_red: GPIO pin for red LED (default: GPIO22)
            led_green: GPIO pin for green LED (default: GPIO27)
            led_blue: GPIO pin for blue LED (default: GPIO24)
        """
        self.buzzer_pin = buzzer_pin
        self.led_red = led_red
        self.led_green = led_green
        self.led_blue = led_blue
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup buzzer
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        GPIO.output(self.buzzer_pin, GPIO.LOW)
        
        # Setup RGB LED
        GPIO.setup(self.led_red, GPIO.OUT)
        GPIO.setup(self.led_green, GPIO.OUT)
        GPIO.setup(self.led_blue, GPIO.OUT)
        
        # PWM for LED brightness control
        self.pwm_red = GPIO.PWM(self.led_red, 100)
        self.pwm_green = GPIO.PWM(self.led_green, 100)
        self.pwm_blue = GPIO.PWM(self.led_blue, 100)
        
        self.pwm_red.start(0)
        self.pwm_green.start(0)
        self.pwm_blue.start(0)
        
        # State
        self.buzzer_active = False
        self.buzzer_thread = None
        self.stop_buzzer_flag = False
        
        print("✅ Hardware alert system initialized")
        print(f"   Buzzer: GPIO{self.buzzer_pin}")
        print(f"   RGB LED: R=GPIO{self.led_red}, G=GPIO{self.led_green}, B=GPIO{self.led_blue}")
    
    def set_led_color(self, red, green, blue):
        """
        Set RGB LED color
        
        Args:
            red: Red intensity (0-100)
            green: Green intensity (0-100)
            blue: Blue intensity (0-100)
        """
        self.pwm_red.ChangeDutyCycle(red)
        self.pwm_green.ChangeDutyCycle(green)
        self.pwm_blue.ChangeDutyCycle(blue)
    
    def led_green(self):
        """Set LED to green (Alert - driver is awake)"""
        self.set_led_color(0, 100, 0)
    
    def led_yellow(self):
        """Set LED to yellow (Warning - drowsiness detected)"""
        self.set_led_color(100, 100, 0)
    
    def led_red(self):
        """Set LED to red (Drowsy - critical alert)"""
        self.set_led_color(100, 0, 0)
    
    def led_off(self):
        """Turn off LED"""
        self.set_led_color(0, 0, 0)
    
    def start_buzzer(self, pattern='continuous'):
        """
        Start buzzer with pattern
        
        Args:
            pattern: 'continuous' or 'beep' (default: continuous)
        """
        if self.buzzer_active:
            return
        
        self.buzzer_active = True
        self.stop_buzzer_flag = False
        
        if pattern == 'continuous':
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
        elif pattern == 'beep':
            self.buzzer_thread = threading.Thread(target=self._beep_pattern, daemon=True)
            self.buzzer_thread.start()
    
    def _beep_pattern(self):
        """Beep pattern: 0.5s on, 0.5s off"""
        while not self.stop_buzzer_flag:
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
            time.sleep(0.5)
    
    def stop_buzzer(self):
        """Stop buzzer"""
        if not self.buzzer_active:
            return
        
        self.stop_buzzer_flag = True
        GPIO.output(self.buzzer_pin, GPIO.LOW)
        self.buzzer_active = False
        
        if self.buzzer_thread:
            self.buzzer_thread.join(timeout=1)
            self.buzzer_thread = None
    
    def update_status(self, confidence, is_drowsy):
        """
        Update hardware based on drowsiness status
        
        Args:
            confidence: Confidence score (0-1)
            is_drowsy: Boolean indicating drowsy state
        """
        if is_drowsy or confidence <= 0.4:
            # RED: Drowsy - activate buzzer
            self.led_red()
            self.start_buzzer(pattern='beep')
        elif confidence <= 0.7:
            # YELLOW: Warning - no buzzer
            self.led_yellow()
            self.stop_buzzer()
        else:
            # GREEN: Alert - all clear
            self.led_green()
            self.stop_buzzer()
    
    def test_hardware(self):
        """Test all hardware components"""
        print("\n🔧 Testing hardware...")
        
        print("Testing GREEN LED...")
        self.led_green()
        time.sleep(1)
        
        print("Testing YELLOW LED...")
        self.led_yellow()
        time.sleep(1)
        
        print("Testing RED LED...")
        self.led_red()
        time.sleep(1)
        
        print("Testing buzzer...")
        self.start_buzzer(pattern='beep')
        time.sleep(2)
        self.stop_buzzer()
        
        print("Turning off...")
        self.led_off()
        
        print("✅ Hardware test complete!")
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.stop_buzzer()
        self.led_off()
        self.pwm_red.stop()
        self.pwm_green.stop()
        self.pwm_blue.stop()
        GPIO.cleanup()
        print("✅ GPIO cleaned up")


# Test script
if __name__ == '__main__':
    print("="*60)
    print("🔔 HARDWARE ALERT SYSTEM TEST")
    print("="*60)
    
    try:
        # Initialize hardware
        alert = HardwareAlert()
        
        # Run test
        alert.test_hardware()
        
        # Simulate drowsiness detection
        print("\n📊 Simulating drowsiness detection...")
        
        print("\n1. Alert state (confidence: 0.85)")
        alert.update_status(0.85, False)
        time.sleep(3)
        
        print("\n2. Warning state (confidence: 0.55)")
        alert.update_status(0.55, False)
        time.sleep(3)
        
        print("\n3. Drowsy state (confidence: 0.25)")
        alert.update_status(0.25, True)
        time.sleep(5)
        
        print("\n4. Back to alert (confidence: 0.90)")
        alert.update_status(0.90, False)
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        alert.cleanup()
        print("\n✅ Test complete!")
