<!DOCTYPE html>
<!-- Main PHP file: Reads status from Intel Joule, generates first page -->

<html>
    <head>
        <meta charset="utf-8" />
        <title>Intel Joule Status</title>
    </head>
 
    <body style="background-color: white;">
    <!-- status and stop/stop pictures -->
	<?php
	$status = array(0,0,0,0,0,0);
	//this php script generate the first page in function of the file
	for ( $i= 1; $i<7; $i++) {

		// Read the status from a text file that has 6 digit number. Each
		// number presentst the LOW/HIGH value of the status check with 
		// the 6th digit representing the start/stop data logging switch
		exec("cut -c".$i." /home/root/status.txt", $status[$i-1] );

		// TO DELETE: 
		//
		// set the pin's mode to output and read them
		// system("gpio mode ".$i." out");
		// exec ("gpio read ".$i, $val_array[$i], $return );
		//
	}
	//Status checks (x5) 
	$i =0;	// IS THIS NECESSARY?
	for ($i = 0; $i < 5; $i++) {
		//if status IS NOT checked
		if ($status[$i][0] == 0 ) {
			echo ("	<img id='check_".$i."' src='images/x.jpg' />");
			echo "\r\n";
		}
		//if status IS checked 
		if ($status[$i][0] == 1 ) {
			echo ("	<img id='check_".$i."' src='images/check.jpg' />");
			echo "\r\n";
		}	 
	}

	//Drone start/stop toggle switch icon 
	if ($status[5][0] == 0) {
		echo ("	<img id='toggle_".$i."' src='images/toggleOff.jpg' />");
	}
	elseif ($status[5][0] == 1) {
		echo ("	<img id='toggle_".$i."' src='images/toggleOn.jpg' />");
	}
	?>
	 
	<!-- javascript -->
	<!--script src="update.js"></script-->
    </body>
</html>