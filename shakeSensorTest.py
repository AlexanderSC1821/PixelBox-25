import RPi.GPIO as GPIO
import time

SENSOR_PIN = 27  # or 16 if you're wired to Pin 36

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

print("Waiting for vibration...")

try:
    while True:
        if GPIO.input(SENSOR_PIN) == GPIO.HIGH:
            print("Shake detected!")
        else:
            print("Idle")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()