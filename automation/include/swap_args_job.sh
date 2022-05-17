#!/bin/bash

# This job passes first argument as second and the sceond as the first
# to the given job.
# Can be used for copy_job when the first argument is automatically provided
# from the parent job like dir_job but should be used as an output path.
swap_args_job()
{
	source log.sh
	local log_prefix="[swap_args_job]: "
	[ -z "$1" ] && log "No agument provided 0 of 3" && exit
	[ -z "$2" ] && log "No agument provided 1 of 3" && exit
	[ -z "$3" ] && log "No job provided 2 of 3" && exit || job_path=$3

	local job=$(basename $job_path)
	source $job
	local jobname=$(echo $job| cut -d. -f1)
	$jobname "$2" "$1" ${@:4}
}

job()
{
	swap_args_job $@
}
