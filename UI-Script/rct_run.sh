# -* bash *-

timestamp() {
    date
}

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

INSTALL_DIR=&INSTALL_PREFIX

source $INSTALL_DIR/etc/rct_config

log="$log_dir/rctstart_rct.log"
led_dir="/sys/class/gpio/gpio$led_num"
switch_dir="/sys/class/gpio/gpio$switch_num"
keep_alive='rct_gps_keep_alive.py'
sdr_starter='rct_sdr_starter'

STATUS=$1

if [ "$STATUS" -eq "1" ]
    then
    stateVal="startWait"
else
    echo "$(timestamp): Complete Status Checks!" >> $log
    exit
fi

stateVal=""

while [ "$STATUS" -eq "1" ]
do
    case $stateVal in
        "startWait")
            $keep_alive -i $mav_port &>> $log_dir/gps_keep.log &
            keep_alive_pid=$!
            switchVal=`cat $switch_dir/value`
            until [ "$switchVal" = "0" ]; do
                sleep 3
                switchVal=`cat $switch_dir/value`
            done
            echo "$(timestamp): Received start signal!" >> $log
            kill -s INT ${keep_alive_pid}
            stateVal="startgo"
            ;;

        "startgo" )
        # State 2 - go for start, initialize
            ${sdr_starter} &
            sdr_starter_pid=$!
            echo "$(timestamp): Started program!" >> $log
            runNum=`rct_getRunNum.py -e $output_dir`
            echo "$(timestamp): $runNum" >> $log
            stateVal="endWait"
            ;;

        "endWait" )
            switchVal=`cat $switch_dir/value`
            until [ "$switchVal" = "1" ]; do
                sleep 3
                switchVal=`cat $switch_dir/value`
            done
            echo "$(timestamp): Received stop signal!" >> $log
            stateVal="endgo"
            ;;
            
        "endgo" )
            kill -s TERM ${sdr_starter_pid}
            # killall ct -s INT
            echo "$(timestamp): Ended program!" >> $log
            echo "$(timestamp): Begin dmesg dump" >> $log
            dmesg >> $log
            echo "$(timestamp): end dmesg dump" >> $log
            # Sync all devices
            sync
            stateVal="startWait"
            ;;
    esac
done            


