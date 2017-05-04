# -* bash *-
#!/bin/sh

timestamp() {
	date
}

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

#Sourcing file to get correct logs and directories
INSTALL_DIR=&INSTALL_PREFIX
source $INSTALL_DIR/etc/rct_config

case "$1" in
    #STATUS will check for correct file and output path, then start checking for GPS lock
    status)
        #Checking for valid output directory
        OUTPUT_CHECK=0
        if [ ! -e $output_dir ]
            then
            echo "$output_dir not found"
            exit 1
        else 
            OUTPUT_CHECK=1
            echo "$output_dir valid"
        fi

        #Check if file exists
        FILE_CHECK=0
        if [ -e "$log_dir/rct_gps_log.log" ] then
            FILE="$log_dir/rct_gps_log.log"
            FILE_CHECK=1
        else
            echo "$log_dir/rct_gps_log.log not a valid file"
            exit 1
        fi

        #Assume parser prints to file line by line
        IFS=$(echo -en "\n\b")
        STATUS_CHECK=0
        exec 3<$FILE
        while read -u 3 -r line
        do
            #read in line by line until we get a "YES" hit and triggers status change
            #Change STATUS_CHECK to 1 when goes through all status checks and passes
            if [ "$line" -eq "YES" ] then
                STATUS_CHECK=1
                echo "GPS lock found!"
                break
            else
                echo "Finding..."
            fi

        done
        ;;

    start)
        # start
        if [ "$STATUS_CHECK" -eq "0" ] then
            echo "GPS Lock not found! Run STATUS to check"
            exit 1
        elif [ "$FILE_CHECK" -eq "0" ] then
            echo "GPS file does not exist! Run STATUS to check"
            exit 1
        elif [ "#OUTPUT_CHECK" -eq "0" ] then
            echo "Confirm OUTPUT_CHECK"
        elif [ ! -f /var/lock/rctstart ] then
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
        exit
        ;;

    restart|reload|condrestart)
        killall rct -r &
        echo "Service started!"
        $INSTALL_DIR/bin/rctrun &
        exit
        ;;
esac

