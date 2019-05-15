import time
import RPi.GPIO as GPIO

def color_read(GrayScale_pin):
    reading = 0
    GPIO.setup(GrayScale_pin, GPIO.OUT)
    GPIO.output(GrayScale_pin, GPIO.LOW)
    time.sleep(0.5)
    GPIO.setup(GrayScale_pin, GPIO.IN)
    while (GPIO.input(GrayScale_pin) == GPIO.LOW):
        reading += 1
    return reading

