#!/bin/bash

source file_utils.sh
source log.sh

last_log_prefix=$log_prefix
log_prefix="[deliver_file_job]: "

deliver_file_job()
{
	[ -z "$1" ] && exit # directory where to deliver
	[ -z "$2" ] && exit # file to deliver into the given directory
	
	# log "cp $2 $1"
	cp $2 $1
}

job()
{
	deliver_file_job $@
}

log_prefix=$last_log_prefix