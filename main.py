import RPi.GPIO as GPIO
import time
import infrared_sensor
import usonic_sensor

#Definition of photoresistor pin
INFRARED_L = 5
INFRARED_R = 6
TRIG_L = 13
ECHO_L = 19
TRIG_R = 23
ECHO_R = 24

def init():
    GPIO.setmode(GPIO.BCM)
    
def main():
    init()
    distance_left = usonic_sensor.check(TRIG_L, ECHO_L)
    distance_right = usonic_sensor.check(TRIG_R, ECHO_R)
    distance_warning = usonic_sensor.warning(distance_left, distance_right)
    print(distance_warning)
    
   #obstacle_position= infrared_sensor.check_obstacle(INFRARED_L, INFRARED_R)

    #if (obstacle_position == 'left'):
      #  print('turn right')
   # elif(obstacle_position == 'right'):
     #   print('turn left')
   # elif(obstacle_position == 'both'):
     #   print('stop')
  #  else:
    #    print('keep going')
        
while True:
    main()
   # time.sleep(0.2)
      
GPIO.cleanup()



    
    
