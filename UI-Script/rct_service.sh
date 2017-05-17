# -* bash *-
### BEGIN INIT INFO
# Provides: rct_service
# Required-Start: $portmap $time $remote_fs
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Performs status check updates
### END INIT INFO
# setup here

PATH=/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

source $INSTALL_DIR/etc/rct_config

# source $INSTALL_DIR/bin/rct_run.sh


# status status_check
# while [ "$status_check" -ne "0" ]
# do
# 	status status_check
# done

# if [ "$status_check" - eq "1" ]
# 	then


case "$1" in
	stop)
		killall rct -r &
		echo "Service stopped!"
		rm -f /var/lock/rctstart
		exit
		;;

	start)
		# start
		if [ ! -f /var/lock/rctstart ]; then
			$INSTALL_DIR/bin/rct_status &
			echo "Service started!"
			touch /var/lock/rctstart
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