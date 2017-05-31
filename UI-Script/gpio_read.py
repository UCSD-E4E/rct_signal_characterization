import sys
import mraa

def main():
	
	gpio_pin = sys.argv[1]
	led = mraa.Gpio(gpio_pin)
	led.dir(mraa.DIR_IN)
	led.read()

if __name__=="__main__":
	main()