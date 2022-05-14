#!/bin/bash

# This job takes a directory and a file as arguments 
# and does a concatenation with the '/' symbol linking them 
# and then pass the result string to the given job passed as a third argument

dir_file_job()
{
	# arguments 
	[ -z "$1" ] && exit # file
	[ -z "$2" ] && exit # directory
	[ -z "$3" ] && exit # job

	source $3
	local job=$(basename $3)
	local jobname=$(echo $job| cut -d. -f1)
	#echo "dir_file_job: $jobname $2/$1 ${@:4}"
	$jobname $2/$1 ${@:4}
}

job()
{
	dir_file_job $@
}
