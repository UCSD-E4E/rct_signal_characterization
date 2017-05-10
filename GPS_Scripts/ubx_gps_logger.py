#!/usr/bin/env python
'''
Parse for 3D fix status, position in lat/long, and GPS time of the week

Usage: ./gps_logger.py [-m <show>] [-o <destination>] [-p <prefix>]
#        [-s <suffix>] [-r <runNum>] [-i port #] [-b baud rate]

'''
import ublox
import argparse
import signal
import re
import os 

def handler(signum, frame):
    global runstate
    runstate = False

signal.signal(signal.SIGINT, handler)

global runstate
print("GPS_LOGGER: Started")
runstate = True

parser = argparse.ArgumentParser(description = "GPS Logging using UBX M8N")
parser.add_argument('-m', '--show', help = 'only print all UBX messages', action='store_true', dest = 'show', required = False, default = False)
parser.add_argument('-o', '--output_dir', help = 'Output directory', metavar = 'data_dir', dest = 'dataDir', required = True)
parser.add_argument('-p', '--prefix', help = 'Output File Prefix, default "GPS_"', metavar = 'prefix', dest = 'prefix', default = 'GPS_')
parser.add_argument('-s', '--suffix', help = 'Output File Suffix, default ""', metavar = 'suffix', dest = 'suffix', default = '')
parser.add_argument('-r', '--run', help = 'Run Number', metavar = 'run_num', dest = 'runNum', required = True, type = int)
parser.add_argument('-i', '--port', help = 'UBX port', metavar = 'port', dest = 'port', required = True)
parser.add_argument('-b', '--baud_rate', help = 'baud rate', metavar = 'baud', dest = 'baud', required = False, default = 57600, type = int)

args = parser.parse_args()
show = args.show 
dataDir = args.dataDir
gpsPrefix = args.prefix
gpsSuffix = args.suffix
runNum = args.runNum
port = args.port
baud = args.baud

# create new GPS log directory if one doesn't already exist 
if not os.path.exists(dataDir):
    os.makedirs(dataDir)

logFile = open("%s/%s%06d" % (dataDir, gpsPrefix, runNum), "w")
logFile.write('Timestamp | Longitude | Latitude | Altitude\n')

dev = ublox.UBlox(port)
while runstate:

    # Parse and format UBX binary messages into a list of fields
    msg = dev.receive_message(ignore_eof=True)
    if msg is None:
        continue 
    msg.unpack()
    ubxMsg = str(msg)
    ubxMsgFields = ubxMsg.split()

    # Print all UBX messages with no logging 
    if show: 
        print ubxMsg 

    # Log GPS fix data
    elif 'NAV_STATUS:' in ubxMsgFields:
        fixFile = open("/var/log/gpsFix.log","a")
        ubxMsgItems = re.split(': |, |=',ubxMsg)
        gpsTime = ubxMsgItems[2]
        if 'gpsFix=3,' in ubxMsgFields:
            fixFile.write('%s True\n' % gpsTime)
        else:
            fixFile.write('%s False\n' % gpsTime)
        fixFile.close()

    # Log position (lat,long,alt) and GPS time 
    elif 'NAV_POSLLH:' in ubxMsgFields:
        ubxMsgItems = re.split(': |, |=',ubxMsg)
        gpsTime = ubxMsgItems[2]
        lon = ubxMsgItems[4]
        lat = ubxMsgItems[6]
        alt = ubxMsgItems[8]
        logFile.write('%s %s %s %s\n' % (gpsTime, lon, lat, alt))
print("GPS_LOGGER: Ending thread")
logFile.close()
