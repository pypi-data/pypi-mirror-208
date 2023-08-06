'''
Please make sure the LED Dot Matrix is connected to the correct pins.
The following table describes how to connect LED Dot Matrix to the 40-pin header.
-----------------------------------------
___MAX7219_______Pin Number_____Pin Name
    VCC             2           5V Power
    GND             34           GND
    DIN             40          GPIO44
    CS              38          GPIO61
    CLK             36          GPIO36
----------------------------------------
'''

import VisionFive.gpio as GPIO
import sys
import time

DIN = 40
CS  = 38
CLK = 36
#Configure the direction of DIN, CS, and CLK as out.
GPIO.setup(DIN, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(CLK, GPIO.OUT)

#Display logo data.
buffer = ['01111000', '01000000', '01111000', '01001111', '01111001', '00001111', '00000001', '00001111']

#LED turn off data.
buffer_off = ['0', '0', '0', '0', '0', '0', '0', '0']

def sendbyte(bytedata):
    for bit in range(0, 8):
        if ((bytedata << bit) & 0x80):
            GPIO.output(DIN, GPIO.HIGH)
        else:
            GPIO.output(DIN, GPIO.LOW)

        #Configure the voltage level of CLK as high.
        GPIO.output(CLK, GPIO.HIGH)
        #Configure the voltage level of CLK as low.
        GPIO.output(CLK, GPIO.LOW)


def WriteToReg(regaddr, bytedata):
    #Configure the voltage level of cs as high.
    GPIO.output(CS, GPIO.HIGH)
    #Configure the voltage level of led_pin as low.
    GPIO.output(CS,GPIO.LOW)
    GPIO.output(CLK, GPIO.LOW)
    sendbyte(regaddr)
    sendbyte(bytedata)
    GPIO.output(CS, GPIO.HIGH)

def WriteALLReg():
    time.sleep(0.1)
    for i in range(0, 8):
        #Write data to register address. Finally the LED matrix displays StarFive logo.
        WriteToReg(i+1, int(buffer[i], 2))
    time.sleep(5)

    #Display logo.
    for i in range(0, 10):
        for j in range(0, 8):
            #Write data to the register address. Finally turn off the LED matrix.
            WriteToReg(j+1, int(buffer_off[j], 2))
        time.sleep(0.1)
        for j in range(0, 8):
            #Write data to the register address. Finally the LED matrix displays with StarFive logo.
            WriteToReg(j+1, int(buffer[j], 2))
        time.sleep(0.1)

def initData():
    WriteToReg(0x09, 0x00) #Set the decode mode.
    WriteToReg(0x0a, 0x03) #Set the brightness.
    WriteToReg(0x0b, 0x07) #Set the scan limitation.
    WriteToReg(0x0c, 0x01) #Set the power mode.
    WriteToReg(0x0f, 0x00) 

def main():
    initData()
    while True:
        WriteALLReg()

if __name__ == "__main__":
    sys.exit(main())
