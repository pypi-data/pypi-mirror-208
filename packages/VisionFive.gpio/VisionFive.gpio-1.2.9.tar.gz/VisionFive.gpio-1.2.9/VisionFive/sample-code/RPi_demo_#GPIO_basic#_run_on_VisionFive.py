#import RPi.GPIO as GPIO            # import RPi.GPIO module  
#*******************************************************
#Note: above command must be replaced with command below
import VisionFive.gpio as GPIO      # import VisionFive.gpio module 
#*******************************************************
from time import sleep             # lets us have a delay  


GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD  
GPIO.setup(36, GPIO.OUT)           # set GPIO27 as an output   
  
try:  
    while True:  
        GPIO.output(36, 1)         # set GPIO27 to 1/GPIO.HIGH/True  
        sleep(0.5)                 # wait half a second  
        GPIO.output(36, 0)         # set GPIO27 to 0/GPIO.LOW/False  
        sleep(0.5)                 # wait half a second  
  
except KeyboardInterrupt:          # trap a CTRL+C keyboard interrupt  
    GPIO.cleanup()                 # resets all GPIO ports used by this program 