#!/bin/bash

# A set of util functions for working with jobs

function extract_job()
{
	# arguments 
	[ -z "$1" ] && echo "No job path provided" && return 1
	
	echo $(basename $1)
	
	return 0
}

function extract_job_name_from_path()
{
	[ -z "$1" ] && echo "No job path or file name provided" && return 1
	echo $(extract_job $1)
	return 0
}

function extract_job_name()
{
	[ -z "$1" ] && echo "No job file name provided" && return 1
	echo $(echo $1| cut -d. -f1)
	return 0
}
