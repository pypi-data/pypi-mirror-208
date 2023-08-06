'''
Please make sure the buttion is connected to the correct pins.
The following table describes how to connect the button to the 40-pin header.
-----------------------------------------
______button_____Pin Number_____Pin Name
    one end          37          GPIO60
  The other end      39            GND
-----------------------------------------
'''

import VisionFive.gpio as GPIO
import sys
import time

key_pin = 37

def main():
    #Configure the direction of key_pin as input.
    GPIO.setup(key_pin, GPIO.IN)
    
    print("*-----------------------Case 1-----------------------------------------------------*")
    print("Note: don't press the key on pin {} once within 5 seconds !!!".format(key_pin))
    print()
    #edge failing can be detected, also set bouncetime(unit: millisecond) to avoid jitter.
    #timeout(unit: millisecond), it means if edge will be detected within timeout time.
    #timeout -1 means  waiting until edge is detected.
    edge_detected = GPIO.wait_for_edge(key_pin, GPIO.FALLING, bouncetime=2, timeout=5000)
    
    
    if edge_detected == key_pin:
        print("Edge has detected within 5 seconds while setting 5 seconds to timeout.")
    else:
        print("Edge hasn't been detected within 5 seconds  while setting 5 seconds to timeout.")
    
    #query if edge event happens.
    edge_detected_flag = GPIO.event_detected(key_pin)

    print("The return value of GPIO.event_detected({}) within 5 seconds: {}".format(key_pin, edge_detected_flag))
    
    print()
    print("*-----------------------Case 2-----------------------------------------------------------------------*")
    print("Please press the key on pin {} once at any time !!!".format(key_pin))
    
    #edge rising can be detected, also set bouncetime(unit: millisecond) to avoid jitter.
    #the default timeout is -1, meaning that waiting until edge is detected.
    edge_detected = GPIO.wait_for_edge(key_pin, GPIO.RISING, bouncetime=2)
    
    if edge_detected == key_pin:
        print("Edge has detected while setting -1 to timeout,")
        print("timeout -1 means waiting until edge is detected.")
    else:
        print("Edge hasn't been detected while setting -1 to timeout,")
        print("timeout -1 means waiting until edge is detected.")
        
    #query if edge event happens.
    edge_detected_flag = GPIO.event_detected(key_pin)
    
    print()
    print("The return value ({}) of GPIO.event_detected({}) should be True.".format(edge_detected_flag, key_pin))
    
    #query if edge event happens.
    edge_detected_flag = GPIO.event_detected(key_pin)
    
    print("The return value ({}) of GPIO.event_detected({}) should be False, because of the secondly reading.".format(edge_detected_flag, key_pin))   

    print()
    


if __name__ == "__main__":
    sys.exit(main())

