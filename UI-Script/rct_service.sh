# -* bash *-
### BEGIN INIT INFO
# Provides: rct_service
# Required-Start: $portmap $time $remote_fs
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Start RCT Payload on switch
### END INIT INFO
# setup here

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

source $INSTALL_DIR/etc/rct_config

case "$1" in
	stop)
		killall rct -r &
		echo "Service stopped!"
		rm -f /var/lock/rct_service
		exit
		;;

	start)
		# start
		if [ ! -f /var/lock/rctstart ]; then
			$INSTALL_DIR/bin/rct_status &
			echo "Service started!"
			touch /var/lock/rct_service
		fi
		exit
		;;

	status)
		# Care about results of the check
		# Just grab what the results were
		# is it running, whats it running, and what are its errors
		if pidof -x "$INSTALL_DIR/bin/rct_status" >/dev/null
            then
            echo "Status currently running!"
        fi
		exit
		;;

	restart|reload|condrestart)
		killall rct -r &
		echo "Service started!"
		$INSTALL_DIR/bin/rctrun &
		exit
		;;
		
esac