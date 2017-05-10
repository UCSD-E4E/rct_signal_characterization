The ubx_gps_logger.py script will parse either a UBX binary file or serial data stream from a UBX GPS module for both 3D GPS fix data from NAV_STATUS messages and position(lat/long) + time from NAV_POSLLH mesages.
The 3D fix GPS data will be logged to /var/log/gpsFix.log, which will require the user to be sudo when running the script.
