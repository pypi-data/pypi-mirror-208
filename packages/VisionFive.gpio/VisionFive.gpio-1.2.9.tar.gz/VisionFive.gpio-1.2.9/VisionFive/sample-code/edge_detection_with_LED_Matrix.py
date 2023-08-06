'''
Step 1:
Please make sure the LED Dot Matrix is connected to the correct pins.
The following table describes how to connect LED Dot Matrix to the 40-pin header.
-----------------------------------------
___MAX7219_______Pin Number_____Pin Name
    VCC             2           5V Power
    GND             34           GND
    DIN             40          GPIO44
    CS              38          GPIO61
    CLK             36          GPIO36
    
Step 2:
Please make sure the button is connected to the correct pins.
The following table describes how to connect the button to the 40-pin header.    
----------------------------------------
_______button____Pin Number_____Pin Name
    one end          37          GPIO60
  The other end      39            GND
-----------------------------------------
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
#Display arabic numeral 5.
buffer_5 = ["00011110", "00010000", "00010000", "00011110", "00000010", "00000010", "00000010", "00011110"]
#Display arabic numeral 4.
buffer_4 = ["00000100", "00001000", "00010000", "00100100", "01000100", "01111111", "00000100", "00000100"]
#Display arabic numeral 3.
buffer_3 = ["00011100", "00100010", "00000010", "00011110", "00000010", "00100010", "00011100", "00000000"]
#Display arabic numeral 2.
buffer_2 = ["00011100", "00100010", "00000010", "00000100", "00001000", "00010000", "00111110", "00000000"]
#Display arabic numeral 1.
buffer_1 = ["00001000", "00001000", "00001000", "00001000", "00001000", "00001000", "00001000", "00001000"]

#LED turn off data.
buffer_off = ['0', '0', '0', '0', '0', '0', '0', '0']

key_pin = 37

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

def disp_clean():
    time.sleep(0.1)
    for i in range(0, 8):
        #Write data to register address. Finally the LED matrix displays StarFive logo.
        WriteToReg(i+1, int(buffer_off[i], 2))
    time.sleep(1)

def disp_numeral_5_to_1():
    for id in range(5, 0, -1):
        buffer_name = "buffer_{}".format(id)
        list_buffer = eval(buffer_name)
        for j in range(0, 8):
            #Write data to the register address. Finally the LED matrix displays with numeral from 5 to 1.
            WriteToReg(j+1, int(list_buffer[j], 2))
        time.sleep(1)
        for j in range(0, 8):
            #Write data to the register address. Finally turn off the LED matrix.
            WriteToReg(j+1, int(buffer_off[j], 2))
        time.sleep(0.1)    

def flash_logo():
    for loop in range(0, 5):
        for j in range(0, 8):
            #Write data to the register address. Finally turn off the LED matrix.
            WriteToReg(j+1, int(buffer_off[j], 2))
        time.sleep(0.1)
        for j in range(0, 8):
            #Write data to the register address. Finally the LED matrix displays with StarFive logo.
            WriteToReg(j+1, int(buffer[j], 2))
        time.sleep(0.1)
        

def WriteALLReg():
    #clean screen
    disp_clean()
    
    #display numeral from 5 to 1
    disp_numeral_5_to_1()

    #falsh starfive logo.
    flash_logo()
    
def initData():
    WriteToReg(0x09, 0x00) #Set the decode mode.
    WriteToReg(0x0a, 0x03) #Set the brightness.
    WriteToReg(0x0b, 0x07) #Set the scan limitation.
    WriteToReg(0x0c, 0x01) #Set the power mode.
    WriteToReg(0x0f, 0x00) 

#the callback function for edge detection
def detect(pin, edge_type):
    WriteALLReg()
        
def main():
    #Configure the direction of key_pin as input.
    GPIO.setup(key_pin, GPIO.IN)
    #Both edge risiong and failing can be detected, also set bouncetime(unit: millisecond) to avoid jitter
    GPIO.add_event_detect(key_pin, GPIO.FALLING, callback=detect, bouncetime=2)
    
    initData()
    
    print("*------------------------------------------------------*")
    print("Please press the key on pin {} to launch !!!".format(key_pin))
    
    while True:
        m = 1

if __name__ == "__main__":
    sys.exit(main())
