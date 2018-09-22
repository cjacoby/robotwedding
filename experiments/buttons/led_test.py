import RPi.GPIO as GPIO
import time

PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT)

while True:
    print ("LED on")
    GPIO.output(PIN, GPIO.HIGH)
    time.sleep(2)

    print ("LED off")
    GPIO.output(PIN, GPIO.LOW)
    time.sleep(1)
