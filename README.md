# RCTSpring2017

General Overview:
Researchers will often put radio collars on animals before releasing them to gather valuable behavioral data. The researchers will periodically track the animal positions and eventually attempt to recover the radio collars. In some places, such as the Cayman Islands and the Dominican Republic, the wilderness is tough terrain to traverse, potentially taking more than an hour to walk a mile. The Radio Collar Tracker project is designed to address this terrestrial problem by taking to the skies and mounting an antenna onto a quadcopter that is then autonomously flown over the area suspected of containing the animals of interest. The system on the copter listens and aggregates pings transmitted by the animals’ radio collars and triangulates their position using GPS data. This allows the researchers to gather the same data while avoiding treacherous terrain in environments remote to any emergency medical services.

This repo contains any and all CSE 145/237D project code utilized during UCSD's academic spring quarter 2017 to improve upon the RCT design. The following improvements will be implemented:

(1) Integrate and parse an external Ublox m8n GPS module into the payload of a new aerial platform, the 3DR Solo. This task will comprise of writing a python script for the Intel Joule, a Linux microcomputer. 

(2) Design a new user interface for starting and stopping data logging with visual indicators of 3D GPS fix. This task will comprise of writing a bash script for the Intel Joule, as well as a script for an external web GUI. The scripts for this section of the project can be found under the scripts subfolder of the repository.

(3) Emulate a radio collar’s power output in various waveforms using a USRP. This task will comprise of utilizing and implementing the open source SDR library GNURadio.

This repo will push its final software deliverables to the main E4E Radio Collar Tracker repo: https://github.com/UCSD-E4E/radio_collar_tracker_drone. The following open source repos are used in this project:

(1) Ublox binary data parsing: https://github.com/tridgeIn/pyUblox

More information about the project can be found at the UCSD E4E website: http://e4e.ucsd.edu/radio-collar-tracker
