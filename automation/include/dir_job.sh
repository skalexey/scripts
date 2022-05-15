#!/bin/bash

# This job takes a directory as the first argument and a list of files
# as the second (size) and third (array) arguments and does the given job
# passed as the fourth argument on every $directory/$file concatenation

dir_job()
{
	# arguments 
	[ -z "$1" ] && exit # directory
	[ -z "$2" ] && exit # relative file list size
	[ -z "$3" ] && exit # relative file list
	[ -z "$4" ] && exit # job

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
	echo "dir_job: list_job ${#file_list[@]} ${file_list[@]} dir_file_job.sh $directory $job ${@:$((job_index+1))}"
	list_job ${#file_list[@]} ${file_list[@]} swap_args_job.sh $directory dir_file_job.sh $job ${@:$((job_index+1))}
}

job()
{
	dir_job $@
}
