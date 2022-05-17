#!/bin/bash

# This job takes a directory as the first argument and a list of files
# as the second (size) and third (array) arguments and does the given job
# passed as the fourth argument on every $directory/$file concatenation

dir_job()
{
	source log.sh
	local log_prefix="[dir_job]: "
	# arguments 
	[ -z "$1" ] && log_error "No directory provided" && exit # directory
	[ -z "$2" ] && log_error "No relative file list size provided" && exit # relative file list size
	[ -z "$3" ] && log_error "No relative file list provided" && exit # relative file list
	[ -z "$4" ] && log_error "No job provided" && exit # job
	# outputs
	# {1} - $directory/$file
	local directory=$1
#	echo "dir_job: dir: $directory"
	local list_size=$2
#	echo "dir_job: list_size: $list_size"
	local list=${@:3}
	local job_index=$((list_size+3))
#	echo "dir_job: job_index: $job_index"
	local job=${!job_index}
#	echo "dir_job: job: $job"
	source list_job.sh
	cmd="list_job ${#file_list[@]} ${file_list[@]} swap_args_job.sh $directory dir_file_job.sh $job ${@:$((job_index+1))}"
	log "command: $cmd"
	$cmd
}

job()
{
	dir_job $@
}
