import RPi.GPIO as GPIO
from time import sleep


moving_speed =0
r_wheel =0
l_wheel =0

tracking_state = [0,0,0,0]
def init_line():
#	GPIO.cleanup()
#    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TrackSensorLeftPin1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TrackSensorLeftPin2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TrackSensorRightPin1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TrackSensorRightPin2,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def line_track( TrackSensorLeftPin2,TrackSensorLeftPin1, TrackSensorRightPin1, TrackSensorRightPin2 ):
    TrackSensorLeftValue2  = GPIO.input(TrackSensorLeftPin2)
    TrackSensorLeftValue1  = GPIO.input(TrackSensorLeftPin1)
    TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
    TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
    buff = [0,0,0,0]
    buff[0]=TrackSensorLeftValue2
    buff[1]=TrackSensorLeftValue1
    buff[2]=TrackSensorRightValue1
    buff[3]=TrackSensorRightValue2
    # print TrackSensorLeftValue2,TrackSensorLeftValue1,TrackSensorRightValue1,TrackSensorRightValue2
    return buff
def tracking_rule(buff,l,m,h):
	global l_wheel
	global r_wheel
	global moving_speed
	if	 buff == [0,1,1,1]:
		l_wheel -=h; r_wheel +=h
	elif buff == [0,0,1,1]:
		l_wheel -=m; r_wheel +=m
	elif buff == [0,0,0,1]:
		l_wheel -=l; r_wheel += l
	elif buff == [1,0,0,1]:
		l_wheel = moving_speed; r_wheel = moving_speed
	elif buff == [1,0,0,0]:
		l_wheel +=l; r_wheel -=l
	elif buff == [1,1,0,0]:
		l_wheel +=m; r_wheel -=m
	elif buff == [1,1,1,0]:
		l_wheel +=h; r_wheel -=h
	elif buff == [0,0,0,0] or buff == [1,1,1,1]:
		return [0,0]
	elif buff == [0,1,1,0]:
		pass
	return [l_wheel,r_wheel]
