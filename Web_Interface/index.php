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
		exec("cut -c".$i." /usr/local/apache2/htdocs/status.txt", $status[$i-1] );
	}

	echo "<div style='display: block;float: left;margin-right: 5px;'>";

	//Status checks (x5) 
	$i =0;	// IS THIS NECESSARY?
	for ($i = 0; $i < 5; $i++) {

		echo "<div class='image' style='display: block;float: left;margin-right: 5px;'>";

		//if status IS NOT checked
		if ($status[$i][0] == 0 ) {
			echo ("	<img id='check_".$i."' src='images/x.jpg' 
				width='175px' height='175px'/>");
			echo "\r\n";
		}
		//if status IS checked 
		if ($status[$i][0] == 1 ) {
			echo ("	<img id='check_".$i."' src='images/check.jpg' width='175px' height='175px' />");
			echo "\r\n";
		}	 

		// add caption based on status #
		if ($i == 0) {
			echo "<div style='display:table-caption;caption-side:bottom;'>Sane Output Directory</div>";
			echo "\r\n";
		}
		else if ($i == 1) {
			echo "<div style='display:table-caption;caption-side:bottom;'>Output Directory Writable</div>";
			echo "\r\n";
		}
		else if ($i == 2) {
			echo "<div style='display:table-caption;caption-side:bottom;'>SDR Verified</div>";
			echo "\r\n";
		}
		else if ($i == 3) {
			echo "<div style='display:table-caption;caption-side:bottom;'>Available Disk Space</div>";
			echo "\r\n";
		}
		else if ($i == 4) {
			echo "<div style='display:table-caption;caption-side:bottom;'>3D GPS Fix</div>";
			echo "\r\n";
		}

		echo "</div>";

	}

	echo "</div>";

	//start/stop toggle switch icon 

	echo "<div class='image' style='display:table;'>";

	if ($status[5][0] == 0) {
		echo ("	<img id='toggle' src='images/toggleOff.jpg' onclick='toggle_switch ();' 
			width='350px' height='190px' />");
		echo "\r\n";
	}
	elseif ($status[5][0] == 1) {
		echo ("	<img id='toggle' src='images/toggleOn.jpg' onclick='toggle_switch ();' 
			width='350px' height='190px'/>");
		echo "\r\n";
	}
	echo "<div style='display:table-caption;caption-side:bottom;'>Toggle Data Logging</div>";
	echo "\r\n";
	echo "</div>";

	?>
	 
	<!-- javascript -->
	<script src="update.js"> </script>
	<script type="text/javascript">status_loop ();</script>
    </body>
</html>