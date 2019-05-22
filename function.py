import spidev,time
import sys,cmd,shlex,types
from mcp2515 import *
import math
###############################################
#define area
SSP =   0x16    
SMV =   0x18
ENC =   0x1E		# get encoder resolution
GENC=   0x1F		# set encoder resolution
SMOD=   0x2A		# set control mode
GMOD=   0x2B		# get control mode
V   =   0x90		#set speet (moving in spped mode, stay in position mode)
GV  =   0x91		#get initial speed
GVE =   0x92		#Get error speed
GSV =   0x93		
SER =   0x39
GER =   0x3A
SPH =   0x33
GPH =   0x34
SPL =   0x35
GPH =   0x36
PO  =   0x98		#set absolte position as robot's position
M   =   0x99		#set absolute tracking position and move
MM  =   0x9E		#set absolute tracking position and wait
MRUN=   0xA0		#start moving to tracking position
MR  =   0x9A		#set relative tracking position and move
MMR =   0x9F		#set relative tracking position and wait
GM  =   0x9B		#start moving to relative tracking position
GME =   0x9C		
GSM =   0x9D		

#AGV parametter:
pi = 3.1415
wheels_distance = 190.0
wheels_radius =50.0
wheels_diameter = 100.0
wheels_encoder = 4000.0
motorLeft = 25
motorRight = 59
wheel_ticLength = wheels_diameter*pi/wheels_encoder
##############################################
hex_send = [0,0,0,0,0,0,0,0]
hex_revc = [0,0,0,0,0,0,0,0]

r_v=0.0;l_v=0.0
r_v_rotate=0; l_v_rotate=0
pi=3.1415
#basic function of Can controller-------------------------------------------------------
spi = spidev.SpiDev(0,0)

def mcp2515_reset():
    tmpc = [0xc0]
    spi.writebytes(tmpc)

def mcp2515_writeReg(addr, val):
    buf = [0x02, addr, val]
    spi.writebytes(buf)

def mcp2515_readReg(addr):
    buf = [0x03, addr, 0x55]
    buf = spi.xfer2(buf)
    return int(buf[2])
#initial setting mcp2515 
def mcp2515_init():
    mcp2515_reset()
    time.sleep(2)
    mcp2515_writeReg(CNF1,CAN_500Kbps)
    mcp2515_writeReg(CNF2,0x80|PHSEG1_3TQ|PRSEG_1TQ)
    mcp2515_writeReg(CNF3,PHSEG2_3TQ)
    mcp2515_writeReg(TXB0SIDH,0xFF)
    mcp2515_writeReg(TXB0SIDL,0xEB)
    mcp2515_writeReg(TXB0EID8,0xFF)
    mcp2515_writeReg(TXB0EID0,0xFF)

    mcp2515_writeReg(RXB0SIDH,0x00)
    mcp2515_writeReg(RXB0SIDL,0x00)
    mcp2515_writeReg(RXB0EID8,0x00)
    mcp2515_writeReg(RXB0EID0,0x00)
    mcp2515_writeReg(RXB0CTRL,0x40)
    mcp2515_writeReg(RXB0DLC,DLC_8)

    mcp2515_writeReg(RXF0SIDH,0xFF)
    mcp2515_writeReg(RXF0SIDL,0xEB)
    mcp2515_writeReg(RXF0EID8,0xFF)
    mcp2515_writeReg(RXF0EID0,0xFF)

    mcp2515_writeReg(RXM0SIDH,0xFF)
    mcp2515_writeReg(RXM0SIDL,0xE3)
    mcp2515_writeReg(RXM0EID8,0xFF)
    mcp2515_writeReg(RXM0EID0,0xFF)

    mcp2515_writeReg(CANINTF,0x00)
    mcp2515_writeReg(CANINTE,0x01)

    mcp2515_writeReg(CANCTRL,REQOP_NORMAL|CLKOUT_ENABLED)

#    tmpc = mcp2515_readReg(CANSTAT)
#    print tmpc
    print '\r\nMCP2515 Initialized.\r\n'

#send a 8 bytes message to Can --- [len] [ID] [Command] [Command] [data] [data] [data] [data]
def mcp2515_write(buf, msgID):
    mcp2515_writeReg(TXB0SIDH, (msgID>>3)&0x1F);
    mcp2515_writeReg(TXB0SIDL, (msgID<<5)&0xE0);
    for i in range(500):
        if not mcp2515_readReg(TXB0CTRL)&0x08:
            break
    N = len(buf)
    for j in range(N):
        mcp2515_writeReg(TXB0D0+j,buf[j])
    mcp2515_writeReg(TXB0DLC,N)
    mcp2515_writeReg(TXB0CTRL,0x08)

#receive a 8 bytes message to Can --- [len] [ID] [Command] [Command] [data] [data] [data] [data]
def mcp2515_read():
    N = 8
    buf = []
    for i in range(N):
        buf.append(mcp2515_readReg(RXB0D0+i+16))
    mcp2515_writeReg(CANINTF,0)
    return buf
#----------------------------------------------------------------------------------------------------
def mcp2515_reader(motorID):
    global hex_send
    buf = []
    dec_to_hex(0)
    a=0
    for i in range(2):
        mcp2515_write(hex_send,motorID)
        buf = mcp2515_read()
        b = get_data(buf)
        if b!=0 and i>0:
            a = b
    return a
#convert from decimal to hecimal to send to MCP 2515 (done)
def dec_to_hex(num):
    heximal = [0,0,0,0,0,0,0,0,0]
    i=0;temp=0
    quot=num
    global hex_send
    while (quot!=0 and i<8):
        temp=quot%16
        heximal[i]=temp
        quot=quot/16
        i+=1
    i=0
    for x in range(5)[5:0:-1]:
        hex_send[8-x] = heximal[i]+heximal[i+1]*16
        i += 2
#convert from heximal to decimal data from mcp2515 (done)
def get_data(hexa=[]):
    a=''
    num = hexa[7]>>7
    if (num != 1):
        for i in range(1,5):
            well=(hex(hexa[8-i])[2:4])
            if (len(well) ==1 ): well = '0' + well
            a += well
        a= '0x'+a
        return int(a,16)
    else:
        for i in range(1,5):
            well=(hex(255-hexa[8-i])[2:4])
            if (len(well) ==1 ): well = '0' + well
            a += well
        a= '0x'+a
        return -int(a,16)-1
#change mode:
def set_mode(mode,motorID):
    if (mode == 'speed'): 
        num = 0
    elif (mode == 'position'):
        num = 256 		
    global hex_send
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= SMOD
    dec_to_hex(num)
    if (num == 256 or num == 0):     
		mcp2515_write(hex_send,motorID)
		print 'change mode done!'
#in mode speed:
def set_speed(num,motorID):
    global hex_send
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= V
    dec_to_hex(num)
    mcp2515_write(hex_send,motorID)
#read the actual speed
def get_speed(motorID):
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= GV
    dec_to_hex(0)
    return mcp2515_reader(motorID)
#in mode position:-------------------------------------------------------------------------------------------
#Reset the absolute position as current position
def set_zero_abs(motorID):
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= PO
    dec_to_hex(0)
    mcp2515_write(hex_send,motorID)
#abs position
def set_abs_position(num,motorID):
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= M
    dec_to_hex(num)
    mcp2515_write(hex_send,motorID)
#relative position
def set_rel_position(num,motorID):
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= MR
    dec_to_hex(num)
    mcp2515_write(hex_send,motorID)
#read position
def read_position(motorID):
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= GM
    dec_to_hex(0)
    return mcp2515_reader(motorID)
# parameter: can ID, command ID, Value(int)
def set_parameter(motorID,cmd,num):
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= cmd
    dec_to_hex(num)
    mcp2515_write(hex_send,motorID)
    return mcp2515_reader(motorID)
#-------------motion in mm/s-- and rad/s--------------------------
def speed_motion(lin,ang):
	global wheels_distance; global wheels_encoder; global wheels_diameter; global pi

	r_v = (2*lin - ang*wheels_distance)/(2.0)
	l_v = (2*lin + ang*wheels_distance)/(2.0)
#	print 'r_v: ',r_v,' l_v: ',l_v
	l_v_rotate = int(l_v*(wheels_encoder/(pi*wheels_diameter)))
	r_v_rotate = int(r_v*(wheels_encoder/(pi*wheels_diameter)))
#	print 'rotating speed: '
#	print 'left wheel: ',l_v_rotate 
#	print 'right wheel: ',r_v_rotate
	set_speed(l_v_rotate,motorLeft)
	set_speed(r_v_rotate,motorRight)
#break motor
def break_motor():
    set_speed(0,0)

#----------------Paramerter setting mode-------------------------
def setting(motorID,paraname,num):
    global hex_send
    if paraname == 'ID':
        para=0x28
    elif paraname =='P':
        para=0x60
    elif paraname == 'I':
        para=0x62
    elif paraname == 'D':
        para=0x64
    elif paraname == 'acceleration':
        para=0x58
    elif paraname == 'encoder':
        para=0x1E
    elif paraname == 'gear ratio':
        para=0x14
    elif paraname == 'max speed':
        para=0x16
    elif paraname == 'min speed':
        para=0x18
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= para
    dec_to_hex(num)
    mcp2515_write(hex_send,motorID)
    save(motorID)

def save(motorID):
    global hex_send
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= 0x82
    dec_to_hex(0)
    mcp2515_write(hex_send,motorID)
def get_parameter(motorID,paraname):
    if paraname == 'ID':
        para=0x29
    elif paraname =='P':
        para=0x61
    elif paraname == 'I':
        para=0x63
    elif paraname == 'D':
        para=0x65
    elif paraname == 'acceleration':
        para=0x59
    elif paraname == 'encoder':
        para=0x1F
    elif paraname == 'gear ratio':
        para=0x15
    elif paraname == 'max speed':
        para=0x17
    elif paraname == 'min speed':
        para=0x19
    global hex_send
    buf = []
    hex_send[0]= 8
    hex_send[1]= motorID
    hex_send[2]= para
    dec_to_hex(0)
    return mcp2515_reader(motorID)
#-----------------------Position mode---------------------------
def angle_turn(ang, w):  #tracking angle and turning speed
    speed_motion(0,w)
    rd =  (pi*wheels_distance)*(ang/(2*pi))/wheel_ticLength
    ld = -(pi*wheels_distance)/(ang/(2*pi))/wheel_ticLength
    set_rel_position(ld,motorLeft)
    set_rel_position(ld,motorRight)
    while (get_speed(motorLeft) != 0 or get_speed(motorRight) != 0):
		pass
    return 'done'

def motor_position(distance,speed):
    speed_motion(speed,0)
    rd = distance/wheel_ticLength
    ld = distance/wheel_ticLength
    set_rel_position(ld,0) #send command to both motor
    while (get_speed(motorLeft) != 0 or get_speed(motorRight) != 0):
		pass
    return 'done'

def point_following(x,y,speed,w):
    ang = atan2(y,x)
    distance = (x**2 +y**2)**0.5
    angle_turn(ang,w)
    motor_position(distance,speed)
    return 'done'
