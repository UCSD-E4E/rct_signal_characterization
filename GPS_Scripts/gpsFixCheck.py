#!/usr/bin/env python
'''Parse for 3D fix and return only when 3D fix has been found'''

import ublox
import signal
import re
import argparse
import sys

def handler(signum, frame):
    global runstate
    runstate = False

def main():

	signal.signal(signal.SIGINT, handler)

	global runstate
	runstate = True

	parser = argparse.ArgumentParser(description = "GPS 3D fix check using UBX protocol")
	parser.add_argument('-i', '--port', help = 'UBX port', metavar = 'port', dest = 'port', required = True)
	parser.add_argument('-b', '--baud_rate', help = 'baud rate', metavar = 'baud', dest = 'baud', required = False, default = 57600, type = int)

	args = parser.parse_args()
	port = args.port
	baudrate = args.baud

	dev = ublox.UBlox(port,baudrate)
	while runstate:

	    # Parse and format UBX binary messages into a list of fields
	    msg = dev.receive_message(ignore_eof=True)
	    if msg is None:
	        continue 
	    msg.unpack()
	    ubxMsg = str(msg)
	    ubxMsgFields = ubxMsg.split()

	    # Return only when 3D fix is acquired 
	    if 'NAV_PVT:' in ubxMsgFields:
	        ubxMsgItems = re.split(': |, |=',ubxMsg)
	        if 'fixType=3,' in ubxMsgFields:
	        	return 0
	        else:
	        	continue 

if __name__ == "__main__":
	sys.exit(main())
