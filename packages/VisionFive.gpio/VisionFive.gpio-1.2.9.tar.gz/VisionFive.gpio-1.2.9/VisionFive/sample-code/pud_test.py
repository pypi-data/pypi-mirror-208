'''
Please make sure the GPIO pin is in a suspended state.
'''

import VisionFive.gpio as GPIO

pin = 31
#Configure the direction of pin as input.

level_dict = {
"0": "LOW",
"1": "HIGH"
}

def pud_test():
    print("*----------------------Start testing------------------------------*")
    print()
    print("Step 1: set input to direction of GPIO pin {}.".format(pin))
    GPIO.setup(pin, GPIO.IN)
    print()
    
    IVAL = GPIO.input(pin)
    IVAL_STR = level_dict[str(IVAL)]
    print("Step 2: the default input level is {}.".format(IVAL_STR))
    print()
    
    print("Step 3.1: set PUD_DOWN to input direction of GPIO pin {}.".format(pin))
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print()
 
    IVAL = GPIO.input(pin)
    IVAL_STR = level_dict[str(IVAL)]
    print("Step 3.2: the input level with pull_down enabled is {}.".format(IVAL_STR))
    print()
    
    print("Step 4.1: set PUD_UP to input direction of GPIO pin {}.".format(pin))
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print()
    
    IVAL = GPIO.input(pin)
    IVAL_STR = level_dict[str(IVAL)]
    print("Step 4.2: the input level with pull_up enabled is {}.".format(IVAL_STR))
    print()
    
    print("*---------------------------end test------------------------------*")


if __name__ == '__main__':
    try:
        pud_test()
        
    finally:
        GPIO.cleanup()

