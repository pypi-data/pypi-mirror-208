'''
Please make sure the LED is connected to the correct pins.
The following table describes how to connect LED to the 40-pin header.
-----------------------------------------
_______LED_________Pin Number_____Pin Name
    Positive          22          GPIO50
    Negative          6            GND
-----------------------------------------
'''

import time
import VisionFive.gpio as GPIO

led_pin = 22

#Configure the direction of led_pin as out.
GPIO.setup(led_pin, GPIO.OUT)
#Configure the voltage level of led_pin as high.
GPIO.output(led_pin, GPIO.HIGH)

#Configure the frequency as 10.
p = GPIO.PWM(led_pin, 10)
#Initialize the duty ratio as 0.
p.start(0)

try:
    #Change the LED blink frequency.
    while True:
        for dc in range(0, 101, 5):
            #Change the duty ratio from 0 to 100. Step size: 5
            p.ChangeDutyRatio(dc)
            time.sleep(1)
        for dc in range(100, -1, -5):
            #Change the duty ratio from 100 to 0. Step size: -5
            p.ChangeDutyRatio(dc)
            time.sleep(1)
except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup(led_pin)
