#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spidev,time
import sys,cmd,shlex,types
from mcp2515 import *

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

def mcp2515_init():
    mcp2515_reset()
    time.sleep(2)
    #Set baud rate 125Kbps
    #Set CNF1,SJW=00, length 1TQ, BRP=49, TQ=[2*(BRP+1)]/Fsoc=2*50/8M=12.5us
    mcp2515_writeReg(CNF1,CAN_500Kbps);
    #set CNF2,SAM=0,Sampling the bus at the sampling point，PHSEG1=(2+1)TQ=3TQ,PRSEG=(0+1)TQ=1TQ
    mcp2515_writeReg(CNF2,0x80|PHSEG1_3TQ|PRSEG_1TQ);
    #set CNF3,PHSEG2=(2+1)TQ=3TQ, and set the CLKOUT pin as the time output enable bit when CANCTRL.CLKEN=1
    mcp2515_writeReg(CNF3,PHSEG2_3TQ);

    mcp2515_writeReg(TXB0SIDH,0xFF)#Transmit buffer 0 standard identifier high
    mcp2515_writeReg(TXB0SIDL,0xEB)#Transmit buffer 0 standard identifier low 
                                   #(the third bit is the transmit extended identifier enable bit)
    mcp2515_writeReg(TXB0EID8,0xFF)#Transmit buffer 0 expands the identifier high
    mcp2515_writeReg(TXB0EID0,0xFF)#Transmit buffer 0 expands the identifier high

    mcp2515_writeReg(RXB0SIDH,0x00)#Clear the standard identifier high of receive buffer 0
    mcp2515_writeReg(RXB0SIDL,0x00)#Clear the standard identifier low of receive buffer 0
    mcp2515_writeReg(RXB0EID8,0x00)#Clear the extended identifier high of receive buffer 0
    mcp2515_writeReg(RXB0EID0,0x00)#Clear the extended identifier high of receive buffer 0
    mcp2515_writeReg(RXB0CTRL,0x40)#Receive only valid information for extended identifiers
    mcp2515_writeReg(RXB0DLC,DLC_8)#Set the length of the received data to 8 bytes.

    mcp2515_writeReg(RXF0SIDH,0xFF)#Configure Acceptance Filter Register n Standard Identifier High
    mcp2515_writeReg(RXF0SIDL,0xEB)#Configure the acceptance filter register n standard identifier low bit 
                                   #(the third bit is the receive extended identifier enable bit)
    mcp2515_writeReg(RXF0EID8,0xFF)#Configure the acceptance filter register n to expand the identifier high
    mcp2515_writeReg(RXF0EID0,0xFF)#Configure the acceptance filter register n to extend the identifier low

    mcp2515_writeReg(RXM0SIDH,0xFF)#Configure Acceptance Mask Register n Standard Identifier High
    mcp2515_writeReg(RXM0SIDL,0xE3)#Configure Acceptance Mask Register n Standard Identifier Low
    mcp2515_writeReg(RXM0EID8,0xFF)#Configure the acceptance filter register n to expand the identifier high
    mcp2515_writeReg(RXM0EID0,0xFF)#Configure the acceptance filter register n to extend the identifier low

    mcp2515_writeReg(CANINTF,0x00)#Clear all bits of the CAN Interrupt Flag Register (must be cleared by the MCU)
    mcp2515_writeReg(CANINTE,0x01)#Configure the receive buffer 0 full interrupt enable of the CAN interrupt enable register. 
                                  #Other bits disable interrupts.

    mcp2515_writeReg(CANCTRL,REQOP_NORMAL|CLKOUT_ENABLED)#Set the MCP2515 to normal mode and exit the configuration mode.

   #tmpc = mcp2515_readReg(CANSTAT)#Read the value of the CAN status register
   #tmpd = int(tmpc[0]) & 0xe0
   #if OPMODE_NORMAL!=tmpd:#Check if MCP2515 has entered normal mode
   # mcp2515_writeReg(CANCTRL,REQOP_NORMAL|CLKOUT_ENABLED)# Set the MCP2515 to XX mode again and exit the configuration mode.
    print '\r\nMCP2515 Initialized.\r\n'


def mcp2515_write(buf, msgID):
    mcp2515_writeReg(TXB0SIDH, (msgID>>3)&0x1F);
    mcp2515_writeReg(TXB0SIDL, (msgID<<5)&0xE0);
    for i in range(50):
        time.sleep(2) #Delayed by software by about nms (inaccurate)
        if not mcp2515_readReg(TXB0CTRL)&0x08:#Read some status instructions quickly and wait for the TXREQ flag to be cleared
            break
    N = len(buf)
    for j in range(N):
        mcp2515_writeReg(TXB0D0+j,buf[j])#Write the data to be sent to the transmit buffer register

    mcp2515_writeReg(TXB0DLC,N)#Write the length of the data to be transmitted in this frame to the transmit length register of the transmit buffer 0.
    mcp2515_writeReg(TXB0CTRL,0x08)#Request to send a message

def mcp2515_read():
    N = 0
    buf = []
    if mcp2515_readReg(CANINTF) & 0x01:
        N = mcp2515_readReg(RXB0DLC)#Read the data length received by Receive Buffer 0 (0~8 bytes)
        for i in range(N):
            buf.append(mcp2515_readReg(RXB0D0+i))#Put the data received by CAN into the specified buffer
    mcp2515_writeReg(CANINTF,0)#Clear interrupt flag bit (interrupt flag register must be cleared by MCU)
    return buf

class MyCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt='wyq@rpi2 ~ $ '
        mcp2515_init()

    def emptyline(self):
        pass

    def do_test(self,arg):
        lex = shlex.shlex(arg)
        for x in lex:
            print x

    def do_exit(self,arg):
        return True

    def do_mcp(self,arg):
        lex = shlex.shlex(arg)
        try:
            for x in lex:
                if x=='-':
                    opt = lex.next()
                    if opt.lower()=='init':
                        mcp2515_init()
                    elif opt.lower()=='w':
                        buf = []
                        for i in lex:
                            buf.append(int(i))
                        ID = 25
                        mcp2515_write(buf,ID)
                    elif opt.lower()=='r':
                        buf = mcp2515_read()
                        print 'Received:',len(buf)
                        for i in buf:
                            print hex(int(i))
                    else:
                        pass
        except BaseException, e:
            print e

    def do_help(self,arg):
        print 'CAN transceiver controller based on MCP2515'
        print 'Author:Wang Yongqiang QQ:917888229 Date:2016-8-18'
        print 'Send: mcp -w XX YY ZZ'
        print 'Read: mcp -r'
        print 'Init: mcp -init'


if __name__=='__main__':
    mycmd = MyCmd()
    mycmd.cmdloop()
