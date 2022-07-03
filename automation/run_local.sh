#!/bin/bash

# This script runs any job passed as a script path forwarding all arguments to it
# Used in two cases:
# 	* to simplify run subjobs calls
#	* to run a job in a separated context (e.x. to be able to call new bash instance from it)

function run_local()
{
	[ -z $1 ] && echo "[run_local]: No job specified" && exit # job

	source job.sh
	local job=$(extract_job "$1")
	source $job

	# call the job
	local jobname=$(extract_job_name "$job")
	$jobname ${@:2}

	return $?
}

run_local $@
