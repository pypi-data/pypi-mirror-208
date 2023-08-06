'''
Please make sure the buzzer is connected to the correct pins.
The following table describes how to connect the buzzer to the 40-pin header.
-----------------------------------------
Passive Buzzer___Pin Number_____Pin Name
    VCC             1         3.3V Power
    GND             6           GND
    I/O             18          GPIO51
-----------------------------------------
'''

import VisionFive.gpio as GPIO
import time

buzz_pin = 18
ErrOutOfRange = 0

def setup():
    #Configure the direction of buzz_pin as out.
    GPIO.setup(buzz_pin, GPIO.OUT)
    #Configure the voltage level of buzz_pin as high.
    GPIO.output(buzz_pin, GPIO.HIGH)

def pitch_in_check():
    val_in = input('Enter Pitch (200 to 20000): ')
    val = float(val_in)

    if 200 <= val <= 20000:
        return val
    else:
        print('The input data is out of range (200 to 20,000 Hz). Please re-enter.')
        return ErrOutOfRange

def loop(pitch, cycle):
    delay = 1.0 / pitch
    cycle = int((cycle * pitch)/2)

    #Buzzer beeps.
    while cycle >= 0:
        GPIO.output(buzz_pin, GPIO.LOW)
        time.sleep(delay)
        GPIO.output(buzz_pin, GPIO.HIGH)
        time.sleep(delay)

        cycle = cycle - 1

def destroy():
    GPIO.output(buzz_pin, GPIO.HIGH)
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        #Input value of pitch (200 to 20,000 Hz).
        pitch = pitch_in_check()
        while pitch == 0:
            pitch = pitch_in_check()

        #Input value of cycle time (seconds).
        cycle_in = input("Enter Cycle (seconds): ")
        cycle = int(cycle_in)

        #The buzzer beeps with the specified pitch and cycle.
        loop(pitch, cycle)
    finally:
        destroy()


