import RPi.GPIO as GPIO
from time import sleep
from function import *

kP = 0 ; kI = 0 ; kD = 0 ; error = 0 ; pre_error = 0 ; _integral =0
moving_speed =0
r_wheel =0
l_wheel =0
double_delay_time=0
sampletime = 0
prev_buff = [0,0,0,0]
def init_line(TrackSensorLeftPin2,TrackSensorLeftPin1, TrackSensorRightPin1, TrackSensorRightPin2):
	GPIO.setup(TrackSensorLeftPin2,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(TrackSensorLeftPin1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(TrackSensorRightPin1,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(TrackSensorRightPin2,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def line_track(TrackSensorLeftPin2,TrackSensorLeftPin1, TrackSensorRightPin1, TrackSensorRightPin2 ):
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
def tracking_rule_PID(buff):
	global l_wheel
	global r_wheel
	global moving_speed
	global prev_buff
	global error
	print buff
	if buff != [1,0,0,1] and buff != [0,1,1,1] and buff != [0,0,0,1] and buff != [0,1,0,0] and buff != [0,0,1,0] and buff != [1,0,0,0] and buff != [1,1,1,0] and buff != [0,0,0,0] and buff != [1,1,1,1] and buff != [1,1,0,0] and buff != [0,0,1,1]:
		print 'UNDEFINE'
		buff = prev_buff
	if buff == [1,0,0,1]:
		error = 0
	elif buff == [1,1,1,0]:
		error = 3
	elif buff == [1,1,0,0]:
		error = 2
	elif buff == [1,0,0,0]:
		error = 1.5
	elif buff == [0,1,0,0]:
		error = 1
	elif buff == [0,0,1,0]:			
		error = -1
	elif buff == [0,0,0,1]:
		error = -1.5
	elif buff == [0,0,1,1]:
		error = -2
	elif buff == [0,1,1,1]:
		error = -3
	pid_val = PID_cal()
	lv = l_wheel + pid_val
	rv = r_wheel - pid_val

	if buff == [0,0,0,0]:
		pass
		error = 0
		prev_buff = buff
		return [0,0,1]
	elif buff == [1,1,1,1]:
		print buff
		error = 0
		l_wheel = moving_speed; r_wheel = moving_speed
		lv = -l_wheel*40/100; rv = -r_wheel*40/100
	prev_buff = buff
	return [int(lv),int(rv),0]

def PID_cal():
	global kP ; global kI ; global kD ; global error ; global pre_error ; global sampletime ; global _integral
	Ppart = kP*error
	_integral += error * sampletime
	Ipart = kI*_integral
	_derivative  = (error  - pre_error )/sampletime
	Dpart  = kD *_derivative
	PID_output = Ppart  + Ipart  + Dpart
	pre_error  = error
	return PID_output
