import os
import sys 
import time
import logging
from PIL import Image
sys.path.append("..")

from  lib import LCD2inch_lib

def main():    
    print('-----------lcd demo-------------')    
  
   
    disp = LCD2inch_lib.LCD_2inch(44, 0, '/dev/spidev0.0')      
    disp.lcd_init()
    image = Image.open('./LCD_2inch.jpg')       
    disp.lcd_ShowImage(image, 0, 0)     
   
    
if __name__=="__main__":
    main()