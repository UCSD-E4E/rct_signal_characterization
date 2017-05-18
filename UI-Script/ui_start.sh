# -* bash *-

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

#Sourcing file to get correct logs and directories
INSTALL_DIR=&INSTALL_PREFIX
source $INSTALL_DIR/etc/rct_config

# Checking for valid output directory
# sudo python ./gpsFixCheck.py -i /dev/ttyACM0 -b 115200 >> /var/log/gpsFix.log

OUTPUT_CHECK=1
FILE_CHECK=1
GPS_LOCK=1
SDR_CHECK=1
DISK_SPACE=1

OVERALL_STATUS=1

timestamp() {
    date
}
	
status () {
	# For each brand new status check, resets check
	# vars, so checking occurs
	# 1's represent condition unfulfilled
	OUTPUT_CHECK=1
	FILE_CHECK=1
	GPS_LOCK=1
	SDR_CHECK=1
	DISK_SPACE=1

	OVERALL_STATUS=1

    while [ "$OVERALL_STATUS" -eq "1" ]
    do
        if [ -w $output_dir ]; then
            echo "$output_dir writeable"
            OUTPUT_CHECK=0
        else 
            OUTPUT_CHECK=1
            echo "$output_dir not writable"
            exit 1
        fi
        if [ -e "/var/log/gpsFix.log" ]; then
            FILE="/var/log/gpsFix.log"
            FILE_CHECK=0
        else
            FILE_CHECK=1
            echo "/var/log/gpsFix.log does not exist"
            exit 1
        fi
        D_SPACE=(df -k "$output_dir" | tail -1 | tr -s ' ' | cut -d' ' -f4)
        if [ "$D_SPACE" -ge "6000000" ]; then
            echo "Sufficient available disk space"
            DISK_SPACE=0
        else
            DISK_SPACE=1
            echo "Not enough disk space. Allocate more"
            exit 1
        fi

        echo "Searching for GPS lock, calling gpsFixCheck.py"
        GPS_LOCK=(python ./gpsFixCheck.py -i /dev/ttyACM0 -b 115200)
        if [ "$GPS_LOCK" -eq "0" ]; then
        	echo "GPS LOCK found"
        else 
        	echo "No Lock"
        fi
        # No longer need this because python script runs until it returns value or timed
        # out by user


        # IFS=$(echo -en "\n\b")
        # exec 3<$FILE
        # while read -u 3 -r line
        # while true # want to just keep reaccessing the file and look at line
        # do
            # IFS=$(echo -en "\n\b")
            # exec 3<$FILE
            # read -u 3 -r line
            # line=$(head -n 1 "$FILE")
            # if [ "$line" -eq "TRUE" ]; then
            #     echo "GPS lock found!"
            #     break
            # else
            #     GPS_LOCK=1
            #     echo "Finding..."
            # fi
        # done
        if ["$OUTPUT_CHECK" -ne "1" ] && [ "#FILE_CHECK" -ne "1" ] && [ "$GPS_LOCK" -ne "1"] 
        	&& [ "$SDR_CHECK" -ne "1"]; then
            $OVERALL_STATUS=1
            echo "All checks complete"
        fi
    done
    if [ "$OVERALL_STATUS" -eq "0" ]; then
        functions()
    fi
}

functions() {
    read -p "Do you with to start, stop, or restart drone?" input
    case "$input" in
        start)
            # start
            if [ "$OVERALL_STATUS" -eq "1" ]; then
            	if [ "$GPS_LOCK" -eq "1" ]; then
                	echo "GPS Lock not found!"
            	fi
            	if [ "$FILE_CHECK" -eq "1" ]; then
                	echo "GPS file does not exist!"
            	fi
            	if [ "$OUTPUT_CHECK" -eq "1" ]; then
                	echo "Confirm writable output"
            	fi
            	if [ "$SDR_CHECK" -eq "1" ]; then
            		echo "Verify working SDR"
            	fi
            	if [ "$DISK_SPACE" -eq "1" ]; then
            		echo "Not enough space"
            	fi
            	exit 1
            fi

            if [ ! -f /var/lock/rctstart ]; then
                $INSTALL_DIR/bin/rctrun &
                echo "Service started!"
                touch /var/lock/rctstart
            fi
            exit
            ;;

        stop)
            killall rct -r &
            echo "Stopping Services!"
            rm -f /var/lock/rctstart
            # When data ceases logging, goes back to check mode
            status()
            exit
            ;;

        restart|reload|condrestart)
            killall rct -r &
            echo "Service restarted!"
            $INSTALL_DIR/bin/rctrun &
            status()
            exit
            ;;
    esac
}

# Run status on initial boot
status()