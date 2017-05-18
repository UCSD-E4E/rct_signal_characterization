# -* bash *-
# PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

#Sourcing file to get correct logs and directories
# INSTALL_DIR=&INSTALL_PREFIX
# source $INSTALL_DIR/etc/rct_config

# Checking for valid output directory
# sudo python ./gpsFixCheck.py -i /dev/ttyACM0 -b 115200 >> /var/log/gpsFix.log
timestamp() {
    date
}

log="./output/rctstatus_rct.log"
output_dir="./output/"
# led_dir="/sys/class/gpio/gpio$led_num"
# switch_dir="/sys/class/gpio/gpio$switch_num"
# keep_alive='rct_gps_keep_alive.py'
# sdr_starter='rct_sdr_starter'
zero=0
OUTPUT_CHECK=0
FILE_CHECK=0
GPS_LOCK=0
SDR_CHECK=0
DISK_SPACE=0

OVERALL_STATUS=0

# # Return a value through __resultvar=$1 (not sure if nessary now)
# __resultvar=$1

# Keeps performming checks until exit is thrown or all checks completed

while true
do

    # check for autostart file!
    # if [ ! -e "/usr/local/etc/rct_autostart" ]
    # then
    #         echo "$(timestamp): Autostart not found!" >> $log
    #         exit 1
    # fi

    # check for writiable output directory
    if [ -w $output_dir ]
    then
        echo "$(timestamp): Output Directory Writeable" >> $log
        OUTPUT_CHECK=1

    else 
        echo "$(timestamp): Output Directory not Writable" >> $log
        OUTPUT_CHECK=0
        exit

    fi

    # Loading SDR
    # sudo uhd_usrp_probe --args="type=b200" --init-only

    # Check for SDR connected via USB (return 1 for invalid/0 for valid)
    # uhd_find_devices --args="type=b200"
    # SDR_CHECK=$!

    # Check for available enough disk space to write to
    D_SPACE=`df -k "$output_dir" | tail -1 | tr -s ' ' | cut -d' ' -f4`
    if [ "$D_SPACE" -ge "6000000" ]
    then
        echo "Checking Disk Space"
        echo "$(timestamp): Sufficient available disk space" >> $log
        DISK_SPACE=1
    else
        echo "Checking Disk Space"
        echo "$(timestamp): Not enough disk space. Allocate more" >> $log
        DISK_SPACE=0
        exit 
    fi

    # Chceking for GPS lock by running python script
    echo "Searching for GPS lock, calling gpsFixCheck.py" >> $log
    # python ./gpsFixCheck.py -i /dev/ttyACM0 -b 115200
    # GPS_LOCK=$!
    if [ "$GPS_LOCK" -eq "0" ]
    then
        echo "Checking GPS Lock"
        echo "$(timestamp): GPS LOCK found" >> $log
    else 
        echo "Checking GPS Lock"
        echo "$(timestamp): No Lock" >> $log
    fi

    # # Switch all checks complete flag to 1
    # if ["$OUTPUT_CHECK" -ne "0" ] && [ "#FILE_CHECK" -ne "0" ] && [ "$GPS_LOCK" -ne "0"] \ 
    #     && [ "$SDR_CHECK" -ne "0"]
    # then
    #     $OVERALL_STATUS=1
    #     # Set stateVal to startWait
    #     stateVal="startWait"
    #     echo "$(timestamp): All checks complete" >> $log
    # fi
    # done
    # $OVERALL_STATUS=1
    # Returns 1 when all checks are performed
    SDR_CHECK=0
    if [ "$SDR_CHECK" -eq "0" ]
    then
        echo "$(timestamp): Verify working SDR" >> $log
    else
        echo "$(timestamp): SDR not valid!" >> $log
        exit 1
    fi

    if [ "$OVERALL_STATUS" -eq "0" ]
        then
        # # Used to return __resultvar with OVERALL_STATUS
        # eval $__resultvar="'$OVERALL_STATUS'"

        # Script is already running
        # if pidof -x "$INSTALL_DIR/bin/rct_run" >/dev/null
        #     then
        #     continue
        # fi
        echo "$(timestamp): Starting rct_run script" >> $log
        ./rct_run.sh
        echo "Killing status script"
        exit
    fi
    # else
    #     if pidof -x "$INSTALL_DIR/bin/rct_run" >/dev/null
    #         then
    #         echo "$(timestamp): Error has occured! Killing rct_run" >> $log
    #         pkill -f rct_run.sh
    #     fi
    # fi
done