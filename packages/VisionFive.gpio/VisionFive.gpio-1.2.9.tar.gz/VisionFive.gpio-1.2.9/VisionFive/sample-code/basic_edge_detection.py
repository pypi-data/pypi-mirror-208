'''
Please make sure the button is connected to the correct pins.
The following table describes how to connect the button to the 40-pin header.
-----------------------------------------
_______button____Pin Number_____Pin Name
    one end          37          GPIO60
  The other end      39            GND
-----------------------------------------
'''

import VisionFive.gpio as GPIO
import sys
import time

key_pin = 37

#the callback function for edge detection
def detect(pin, edge_type):
    if (1 == edge_type):
        print("*-----------------------------------*")
        print("Rising edge is detected on pin {} !".format(pin))
    elif (2 == edge_type):
        print("*-----------------------------------*")
        print("Failing edge is detected on pin {} !".format(pin))
    print()


def main():
    #Configure the direction of key_pin as input.
    GPIO.setup(key_pin, GPIO.IN)
    
    #############################
    #edge failing can be detected
    #############################
    GPIO.add_event_detect(key_pin, GPIO.FALLING)
    
    #query if edge event happens
    edge_detected = GPIO.event_detected(key_pin)
    
    #remove detection for edge event
    GPIO.remove_event_detect(key_pin)
    
    #edge failing can be detected, also set bouncetime(unit: millisecond) to avoid jitter
    GPIO.add_event_detect(key_pin, GPIO.FALLING, callback=detect, bouncetime=2)
    
    #remove detection for edge event
    GPIO.remove_event_detect(key_pin)
    
    #edge rising can be detected, also set bouncetime(unit: millisecond) to avoid jitter
    GPIO.add_event_detect(key_pin, GPIO.RISING, callback=detect, bouncetime=2)
    
    #remove detection for edge event
    GPIO.remove_event_detect(key_pin)
    
    print("*-----------------------Case 1-------------------------*")
    print("Please press the key on pin {} once at any time !!!".format(key_pin))
    
    #Both edge risiong and failing can be detected, also set bouncetime(unit: millisecond) to avoid jitter
    GPIO.add_event_detect(key_pin, GPIO.BOTH, callback=detect, bouncetime=2)
    
    while True:
        i = 1;

if __name__ == "__main__":
    sys.exit(main())

