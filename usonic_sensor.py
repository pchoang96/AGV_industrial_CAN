import RPi.GPIO as GPIO
import time

def setup_sonic(trig, echo):
    GPIO.setup(trig, GPIO.OUT,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(echo, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    
    GPIO.output(trig,False)
    GPIO.output(trig,False)
    
    #Waiting For Sensor To Settle
    time.sleep(0.5)
def	check_distance(trig, echo):
    GPIO.output(trig,True)
    GPIO.output(trig,True)
    time.sleep(0.00001)
    GPIO.output(trig,False)
    GPIO.output(trig,False)

    pulse_end = pulse_start = 0
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance= pulse_duration * 17150
    distance = round(distance, 2)
    
    #print(distance, "cm")
    return distance
