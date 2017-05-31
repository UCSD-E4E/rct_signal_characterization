import mraa
import time
import sys

def main():
	led_num = sys.argv[1]
	# Use LEDs GPIO 12, 14, 16, 18, 20
	led = mraa.Gpio(led_num)
	# Set LED to be output
	led.dir(mraa.DIR_OUT)
	# Write 1 to the LED
	led.write(1)
	
if __name__=="__main__":
	main()
