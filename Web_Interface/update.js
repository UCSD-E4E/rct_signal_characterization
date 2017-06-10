// Update web interface page depending on status check changes and toggle switch.
// User can now interact with toggle switch on web interface. 

//Status checks and toggle 
var sane_output     = document.getElementById("check_0");
var output_writable = document.getElementById("check_1");
var verify_SDR      = document.getElementById("check_2");
var disk_space	    = document.getElementById("check_3");
var gps_lock        = document.getElementById("check_4");
var toggle	        = document.getElementById("toggle");

//Create an array of status checks for easy access later
var Status_checks = [ sane_output, output_writable, verify_SDR, disk_space, gps_lock ];

//This function is asking for gpio.php, receiving datas and updating the index.php pictures
function toggle_switch () {
var data = 0;
//send the pic number to gpio.php for changes
//this is the http request
	var request = new XMLHttpRequest();
	request.open( "GET" , "toggle.php", true);
	request.send(null);
	//receiving informations
	request.onreadystatechange = function () {
		if (request.readyState == 4 && request.status == 200) {
			data = request.responseText;
			//update the index pic
			if ( data == "0" ) {
				toggle.src = "images/toggleOff.jpg";
			}
			else if ( data == "1" ) {
				toggle.src = "images/toggleOn.jpg";
			}
			else if ( !(data.localeCompare("fail"))) {
				alert ("Data returned 'fail'" );
				return ("fail");			
			}
			else {
				alert ("Default fail: No other data if condition was met!" );
				return ("fail"); 
			}
		}
		//test if fail
		else if (request.readyState == 4 && request.status == 500) {
			alert ("server error");
			return ("fail");
		}
		//else 
		else if (request.readyState == 4 && request.status != 200 && request.status != 500 ) { 
			alert ("Default fail: Success 200 or General Fail 500 Not Found Though");
			return ("fail"); }
	}	
	
return 0;
}

// Calls status_check every 1 seconds 
function status_loop () {
	setInterval(status_check, 500);
}

//Called by status_loop.
//This function is asking for status.php, receiving status value, and updating the status icons
function status_check () {
	var data = 0; 

	//this is the http request
	var request = new XMLHttpRequest();
	request.open( "GET" , "status.php", true);
	request.send(null);
	//receiving informations
	request.onreadystatechange = function () {
		if (request.readyState == 4 && request.status == 200) {
			data = request.responseText;

			console.log(data);

			// Loop through each status value and change pics accordingly 
			for (i = 0; i <6; i++) {

				// update toggle switch icon if user toggled physical switch 
				if (i == 5) {
					if ( data.charAt(i) == "0" && toggle.src != "images/toggleOff.jpg") {
						toggle.src = "images/toggleOff.jpg";
					}
					else if ( data.charAt(i) == "1" && toggle.src != "images/toggleOn.jpg" ) {
						toggle.src = "images/toggleOn.jpg"; 
					}
				}

				// update status check icons 
				else if ( data.charAt(i) == "0" && Status_checks[i].src != "images/x.jpg") {
					Status_checks[i].src = "images/x.jpg";
				}
				else if ( data.charAt(i) == "1" && Status_checks[i].src != "images/check.jpg" ) {
					Status_checks[i].src = "images/check.jpg";
				}
				else {
					alert ("Default fail: No other data if condition was met!" );
					return ("fail"); 
				}	
			}
		}

		//test if fail
		else if (request.readyState == 4 && request.status == 500) {
			alert ("server error");
			return ("fail");
		}
		//else 
		else if (request.readyState == 4 && request.status != 200 && request.status != 500 ) { 
			alert ("Default fail: Success 200 or General Fail 500 Not Found Though");
			return ("fail"); }

		}		
	//}	
	
return 0;
}
