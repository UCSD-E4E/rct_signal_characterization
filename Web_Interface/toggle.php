<?php
//This page is requested by the updates.js, it updates the status.txt for the 
// toggle switch. 

// Read the toggle value from status.txt
exec("cut -c6 /usr/local/apache2/htdocs/status.txt", $toggleValue, $return );

// Switch toggle on or off 
if ($toggleValue[0] == "0" ) { 
	$toggleValue[0] = "1";
	exec("cat /usr/local/apache2/htdocs/status.txt",$status);
	$status = implode('',$status);
	$status = substr($status, 0, -1)."1";
}
else if ($toggleValue[0] == "1" ) { 
	$toggleValue[0] = "0"; 
	exec("cat /usr/local/apache2/htdocs/status.txt",$status);
	$status = implode('',$status);
	$status = substr($status, 0, -1)."0";
}
system("echo ".$status." > /usr/local/apache2/htdocs/status.txt");

//print toggle value to the client on the response
echo($toggleValue[0]);
?>