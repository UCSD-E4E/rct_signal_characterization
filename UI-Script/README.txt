To integrate these series of the script into the project, 

1) rct_service.sh serves as the old rctstart.sh
	This services will start with boot and upon start
	will call rct_status.sh

2) rct_status.sh and rct_run.sh are two parts of the finite 
	state machine described. rct_status.sh will perform all of
	the status checks in parallel and upon complete checks it will
	terminate and call rct_run then wait for the users start command.
	If the checks fail, the script will throw error and all checks will cease

	To integrate with the original E4E RCT project, rct_status and rct_run
	will replace the old rctrun.sh