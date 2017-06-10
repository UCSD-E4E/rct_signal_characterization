import sys, os
import time
import mraa
# Initialize off
leds = [mraa.Gpio(100), mraa.Gpio(101), mraa.Gpio(102), mraa.Gpio(103)]
for led in leds:
	led.dir(mraa.DIR_OUT)
	led.write(0)

fp = open('status.txt')
while 1:
	time.sleep(0.5)
	data = fp.read()
	status_line = data.split('\n', 1)[0]
	# if status_line[0] == 1:
	# 	led0 = mraa.Gpio(100)
	# 	led0.dir(mraa.DIR_OUT)
	# 	led0.write(1)

	# if status_line[1] == 1:
	# 	led1 = mraa.Gpio(101)
	# 	led1.dir(mraa.DIR_OUT)
	# 	led1.write(1)

	# if status_line[2] == 1:
	# 	led2 = mraa.Gpio(102)
	# 	led2.dir(mraa.DIR_OUT)
	# 	led2.write(1)
		
	# if status_line[3] == 1:
	# 	led3 = mraa.Gpio(103)
	# 	led3.dir(mraa.DIR_OUT)
	# 	led3.write(1)
		
	# if status_line[4] == 1:
	# 	led4 = mraa.Gpio(104)
	# 	led4.dir(mraa.DIR_OUT)
	# 	led4.write(1)
		
	if status_line[5] == 1:
		led5 = mraa.Gpio(100)
		led5.dir(mraa.DIR_OUT)
		led5.write(1)
		

fp.close()
