
This package provides a Python module to control the GPIO on a VisionFive.

Support basic GPIO function including edge detection, I2C API, PWM API, SPI API。

Support python sample, such as:
		GPIO basic operation including input and output
		Sense HAT(B) basing I2C API
		LED_Matrix to display logo about Starfive
		uart_gps_demo to read gps information from GPS NEO-6M
		pwm_led to test PWM module works well
		edge_detection_basic about basic edge API usage
		edge_with_waiting_time about edge detection with specific time
		edge_with_LED_Matrix about trigger LED display by button
		RPi_demo_#GPIO_basic#_run_on_VisionFive about running RPi GPIO demo on VisionFive board
		RPi_demo_#PWM#_run_on_VisionFive about running RPi PWM demo on VisionFive board

how to use VisionFive.gpio API
"``>>>``"

>>> import VisionFive.gpio as GPIO
>>> help(GPIO)
>>> help(GPIO.setup)

how to use VisionFive.gpio PWM API
"``>>>``"

>>> import VisionFive.gpio as GPIO
>>> help(GPIO.PWM)
>>> help(GPIO.PWM.start)


how to use VisionFive.i2c API
"``>>>``"

>>> import VisionFive.i2c as I2C
>>> help(I2C)
>>> help(I2C.open)


how to use VisionFive.spi API
"``>>>``"

>>> import VisionFive.spi as SPI
>>> help(SPI)
>>> help(SPI.setmode)

how to use basic gpio API
"``>>>``"

>>> import VisionFive.gpio as GPIO
>>> import VisionFive.i2c as I2C
>>> 
>>> GPIO.setup(37, GPIO.OUT)
>>> GPIO.output(37, GPIO.HIGH)
>>> GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
>>> GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)
>>> IVAL = GPIO.input(37)
>>> 
>>> p = GPIO.PWM(37, 10)
>>> p.start(20)
>>> p.ChangeDutyRatio(50)
>>> p.ChangeFreq(20)
>>> p.stop()
>>> 
>>> 
>>> GPIO.setup(key_pin, GPIO.IN)
>>> GPIO.add_event_detect(37, GPIO.FALLING)
>>> GPIO.remove_event_detect(37)
>>> 
>>> edge_detected = GPIO.wait_for_edge(key_pin, GPIO.FALLING, bouncetime=2, timeout=5000)
>>> 
>>> #read and write data with i2c 
>>> I2C_DEVICE = "/dev/i2c-1"
>>> SHTC3_I2C_ADDRESS = 0x70
>>> ret = I2C.open(I2C_DEVICE, SHTC3_I2C_ADDRESS)
>>> 
>>> def SHTC3_WriteCommand(cmd):
>>> 	buf0 =  (cmd >> 8)& 0xff
>>> 	buf1 = cmd & 0xff
>>> 	buf = [buf0, buf1]
>>> 	I2C.write(buf)
>>> 
>>> SHTC3_WriteCommand(0x401A)
>>> SHTC3_WriteCommand(0x7866)
>>> buf_list = I2C.read(3)
>>> I2C.close()
>>> 
>>> how to read and write data about ADXL345
>>> SPI.getdev('/dev/spidev1.0')
>>> SPI.setmode(500000, 3, 8)
>>> #set 0xaa to reg 0x1e 
>>> SPI.write([0x1e,0xaa])
>>> #read value of reg 0x1e
>>> SPI.write([0x9e, 0x00])
>>> SPI.read(1)
>>> SPI.freedev()




