#!/usr/bin/env python
'''
Parse for 3D fix from Ublox GPS module via serial or ubx binary file.

Usage: gpsFix_parse.py [--show] <file/serial port>

The --show option is to show NAV_SOL messages containing GPS fix data.

'''
import ublox, sys, fnmatch, os

from optparse import OptionParser

parser = OptionParser("ublox_test.py [options] <file>")
parser.add_option("--show", action='store_true', default=False, help='Show all UBX messages')

(opts, args) = parser.parse_args()

for f in args:
    if opts.show:
        print('Printing all UBX messages from %s' % f)
    else:
        print('Parsing %s for GPS 3D fix' % f)
    dev = ublox.UBlox(f)
    with open('/var/log/gpsFix.log','a') as log:
        while True:

            # Parse and format UBX binary messages into a list of fields
            msg = dev.receive_message()
            if msg is None:
                break
            buf1 = msg._buf[:]
            msg.unpack()
            ubxMsg = str(msg)
            ubxMsgFields = ubxMsg.split()

            # Print the entire NAV_SOL message if user specified option
            if opts.show: 
                if 'NAV_SOL:' in ubxMsgFields:
                    print ubxMsg
                    continue 

            # Print GPS fix data from NAV_SOL
            elif 'NAV_SOL:' in ubxMsgFields:
                if 'gpsFix=0,' in ubxMsgFields:
                    log.write('GPS_FIX: 0 NO FIX\n')
                elif 'gpsFix=1,' in ubxMsgFields:
                    log.write('GPS_FIX: 1 DEAD RECKONING\n') 
                elif 'gpsFix=2,' in ubxMsgFields:
                    log.write('GPS_FIX: 2 2D FIX\n')
                elif 'gpsFix=3,' in ubxMsgFields:
                    log.write('GPS_FIX: 3 3D FIX\n')
                elif 'gpsFix=4,' in ubxMsgFields:
                    log.write('GPS_FIX: 4 DEAD RECKONING\n')
                elif 'gpsFix=5,' in ubxMsgFields:
                    log.write('GPS_FIX: 5 TIME ONLY\n')
                else:
                    log.write('GPS_FIX: ERROR NO GPS FIX DATA')
