//TheFreeElectron 2015, http://www.instructables.com/member/TheFreeElectron/
//JavaScript, uses pictures as buttons, sends and receives values to/from the Rpi
//These are all the buttons
var button_0 = document.getElementById("button_0");	//LED1
var button_1 = document.getElementById("button_1");	//LED2?
var button_2 = document.getElementById("button_2");	//LED3?
var button_3 = document.getElementById("button_3");	//LED4?
var button_4 = document.getElementById("button_4");	//LED5?
var button_5 = document.getElementById("button_5");	//toggle

//Create an array for easy access later
var Buttons = [ button_0, button_1, button_2, button_3, button_4, button_5, button_6];

//This function is asking for gpio.php, receiving datas and updating the index.php pictures
function change_status ( pic ) {
var data = 0;
//send the pic number to gpio.php for changes
//this is the http request
	var request = new XMLHttpRequest();
	request.open( "GET" , "index.php?pic=" + pic, true);
	request.send(null);
	//receiving informations
	request.onreadystatechange = function () {
		if (request.readyState == 4 && request.status == 200 && pic != 5) {
			data = request.responseText;
			//update the index pic
			if ( !(data.localeCompare("0")) ){
				Buttons[pic].src = "img/red/x.jpg";
			}
			else if ( !(data.localeCompare("1")) ) {
				Buttons[pic].src = "img/green/check.jpg";
			}
			else if ( !(data.localeCompare("fail"))) {
				alert ("Something went wrong!" );
				return ("fail");			
			}
			else {
				alert ("Something went wrong!" );
				return ("fail"); 
			}
		}
		// else if (pic == 5) {
		// 	if( !(data.localeCompare("0")) ) {
		// 		Buttons[pic].src = "img/toggle/toggle_0.jpg";
		// 	}
		// 	else if ( !(data.localeCompare("1")) ) {
		// 		Buttons[pic].src = "img/toggle/toggle_1.jpg";
		// 	}
		// }

		//test if fail
		else if (request.readyState == 4 && request.status == 500) {
			alert ("server error");
			return ("fail");
		}
		//else 
		else if (request.readyState == 4 && request.status != 200 && request.status != 500 ) { 
			alert ("Something went wrong!");
			return ("fail"); }
	}	
	
return 0;
}