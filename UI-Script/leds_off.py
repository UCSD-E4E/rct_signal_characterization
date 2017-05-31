import mraa
import time
import sys

def main():
	# Define LEDS from expansion board
	leds = [mraa.Gpio(12), mraa.Gpio(14), mraa.Gpio(16), mraa.Gpio(18), mraa.Gpio(20)]
	for led in leds:

		led.dir(mraa.DIR_OUT)	# set GPIO to be output

		led.write(0)			# Turn LED's off


if __name__=="__main__":
	main()