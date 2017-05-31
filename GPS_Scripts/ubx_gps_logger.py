#!/usr/bin/env python
'''
Parse for 3D fix status, position in lat/long, and GPS time of the week

Usage: ./gps_logger.py [-m <show>] [-o <destination>] [-p <prefix>]
        [-s <suffix>] [-r <runNum>] [-i port #] [-b baud rate]

'''

# TODO: check if UBX library exposes week for GPS time of week
# TODO: add vx, vy, vz, relative alt, heading to gps logging 

import ublox
import argparse
import signal
import re
import os 
import time 

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

# create an offset for global timestamp
ref_time = time.time()
gps_time = 0
offset = gps_time - ref_time 

# use boolean variable to read in initial altitude for relative altitude headings
firstParse = True

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

    # Log position (lat,long,alt) and GPS time 
    elif 'NAV_PVT:' in ubxMsgFields:
        ubxMsgItems = re.split(': |, |=',ubxMsg)
        local_timestamp = time.time()
        global_timestamp = local_timestamp + offset 
        lon = ubxMsgItems[17]
        lat = ubxMsgItems[18]
        alt = ubxMsgItems[19]

        # Assuming first altitude parse is drone ground elevation
        if firstParse == True:
            rel_alt = 0
            init_alt = alt 
            firstParse = False 
        else:
            print str(alt)
            exit()
            rel_alt = float(alt) - float(init_alt)

        # NED velocity
        # TODO: check for translation of NED to XYZ 
        vx = ubxMsgItems[23]
        vy = ubxMsgItems[24]
        vz = ubxMsgItems[25]

        # heading of motion 
        hdg = ubxMsgItems[27]

        logFile.write('%.3f, %s, %s, %.3f, %s, %s, %s, %s, %s, %s\n' % (local_timestamp,\
         lat, lon, global_timestamp, alt, rel_alt, vx, vy, vz, hdg))

print("GPS_LOGGER: Ending thread")
logFile.close()
