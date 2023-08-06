#!/usr/bin/python
'''
Please make sure the 2.4inch LCD Moudle is connected to the correct pins.
The following table describes how to connect the 2.4inch LCD Module to the 40-pin header.
-------------------------------------------------
__2.4inch LCD Module___Pin Number_____Pin Name
    VCC                  17           3.3 V Power
    GND                  39             GND
    DIN                  19           SPI MOSI
    CLK                  23           SPI SCLK
    CS                   24           SPI CE0
    DC                   40            GPIO44
    RST                  11            GPIO42
    BL                   18            GPIO51
-------------------------------------------------
'''

import os
import sys 
import time
import logging
from PIL import Image
sys.path.append("..")

import VisionFive.boardtype as board_t
from  lib import LCD2inch4_lib

'''
Demo modification ans new function description
------------------------------------------------------------
  I.   add the clear() function to fill LCD screen with white
  II.  give a hexadecimal value of white
  III. cycle through multiple pictures
---------------------------------------------------------------
'''

WHITE = 0xFF

def main():    
    print('-----------lcd demo-------------')    

    #Determining cpu Type: 1 means visionfive1; 2 means visionfive 2 
    vf_t = board_t.boardtype()
    if vf_t == 1:
        SPI_DEVICE = "/dev/spidev0.0"
    elif vf_t == 2:
        SPI_DEVICE = "/dev/spidev1.0"
    else:
        print('This module can only be run on a VisionFive board!')
        return 0
  
    """The initialization settings of 2inch and 2.4inch are distinguished"""
    disp = LCD2inch4_lib.LCD_2inch4(11, 40, SPI_DEVICE)      
    #disp.lcd_init()
    disp.lcd_init_2inch4()

    disp.lcd_clear(WHITE)
    
    if vf_t == 1:
        image = Image.open('./visionfive.bmp')
    elif vf_t == 2:
        image = Image.open('./visionfive2.bmp')
    else:
        return

    disp.lcd_ShowImage(image, 0, 0)
    time.sleep(2)

    """add the part of displaying pictures circularly"""
    while True:
        print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))

        """rotate the picture 90 degrees anticlockwise"""
        """to keep consistent with the display direction of other pictures"""
        image = Image.open('./LCD_2inch4_parrot.bmp')
        image = image.transpose(Image.Transpose.ROTATE_90)
        disp.lcd_ShowImage(image, 0, 0)

        image = Image.open('./LCD_2inch.jpg')
        disp.lcd_ShowImage(image, 0, 0)
   
    
if __name__=="__main__":
    main()
