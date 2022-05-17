#!/bin/bash

# This job takes a directory and a file as arguments 
# and does a concatenation with the '/' symbol linking them 
# and then pass the result string to the given job passed as a third argument

dir_file_job()
{
	source log.sh
	local log_prefix="[dir_file_job]: "

	# arguments 
	[ -z "$1" ] && log_error "No directory specified" && exit # directory
	[ -z "$2" ] && log_error "No file specified" && exit # file
	[ -z "$3" ] && log_error "No job specified" && exit # job

	local job=$(basename $3)
	source $job
	local jobname=$(echo $job| cut -d. -f1)
	#log "dir_file_job: $jobname $2/$1 ${@:4}"
	$jobname $1/$2 ${@:4}
}

job()
{
	dir_file_job $@
}
