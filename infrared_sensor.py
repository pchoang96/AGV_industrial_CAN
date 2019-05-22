import RPi.GPIO as GPIO

def init_ir(infrared_sensor_pin):
    GPIO.setup(infrared_sensor_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
def check_obstacle(infrared_sensor_pin):
    obstacle = GPIO.input(infrared_sensor_pin)  
    is_obstacle = False
    if (obstacle == 0):
        is_obstacle = True
    else:
        is_obstacle = False

    return obstacle
