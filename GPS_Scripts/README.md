The gpsFix_parse.py script will parse either a UBX binary file or serial data stream from a UBX GPS module for GPS fix data. 
This data will be logged to /var/log/gpsFix.log, which will require the user to be sudo when running the script.
The script will also show all NAV_SOL messages with any GPS fix data if the script is run with the --show option. 
