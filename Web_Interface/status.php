<?php
// This page is requested by the updates.js, it reads status.txt on the Intel 
// Joule
	
// Read the  value from status.txt
exec("cat /usr/local/apache2/htdocs/status.txt", $status );

//prints status to the client on the response
echo($status[0]);

?>