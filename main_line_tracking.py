from function import *
import line_tracking as track
import infrared_sensor as ir
import usonic_sensor as sonic
import RPi.GPIO as GPIO
from time import sleep
#TrackSensorLeftPin1 TrackSensorLeftPin2 TrackSensorRightPin1 TrackSensorRightPin2
#      3                 5                  4                   18
TrackSensorLeftPin2  =  2   #The second tracking infrared sensor pin on the left is connected to  BCM port 5 of Raspberry pi
TrackSensorLeftPin1  =  14   #The first tracking infrared sensor pin on the left is connected to  BCM port 3 of Raspberry pi
TrackSensorRightPin1 =  4   #The first tracking infrared sensor pin on the right is connected to  BCM port 4 of Raspberry pi
TrackSensorRightPin2 =  17  #The second tracking infrared sensor pin on the right is connected to  BCMport 18 of Raspberry pi

infra_left
infra_right

sonic_left 
sonic_left_trig 23		#sonic trigger pin: GPIO 23
sonic_left_echo 24		#sonic echo pin: GPIO 24
#check_distance(sonic_left_trig,sonic_left_echo)

sonic_right
sonic_right_trig 25		#sonic trigger pin: GPIO 25
sonic_right_echo 8		#sonic echo pin: GPIO 8
#check_distance(sonic_right_trig,sonic_right_echo)

#SPI-mcp2515 pin:
"""
mcp2515			Raspberry

VCC		---		5V pin
GND		---		GND
SI		---		MOSI/GPIO 10
SO		---		MISO/GPIO 9
SCK/CLK	---		SCLK/GPIO 11
CS		---		CS0/GPIO 8
"""
track.moving_speed=500
track.r_wheel = 500
track.l_wheel = 500
          #---trackSensorLeftValue2/|TrackSensorLeftValue1||TrackSensorRightValue1||TrackSensorRightValue2--------------
def init_all():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TrackSensorLeftPin2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TrackSensorLeftPin1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TrackSensorRightPin1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TrackSensorRightPin2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	sonic.setup_sonic(sonic_left_trig,sonic_left_echo)
	sonic.setup_sonic(sonic_right_trig,sonic_right_echo)
    mcp2515_init()

#main programs---------------------------------------------------------------------

init_all()
try:
	while True:
		for i in 3:
			line = track.line_track(TrackSensorLeftPin2, TrackSensorLeftPin1,  TrackSensorRightPin1, TrackSensorRightPin2)
			speed = track.tracking_rule(line,5,10,15)
			spdLeft=speed[0]
			spdRight=speed[1]
			set_speed(spdLeft,motorLeft)
			set_speed(spdRight,motorRight)
			time.sleep(0.02)
			pass
			sonicLeft = check_distance(sonic_left_trig,sonic_left_echo)
			sonicRight = check_distance(sonic_right_trig,sonic_right_echo)
		while a <=20 and b<=20:
			check_distance(sonic_left_trig,sonic_left_echo)
			check_distance(sonic_right_trig,sonic_right_echo)
			time.sleep(0.02)
except KeyboardInterrupt:
	GPIO.cleanup()
