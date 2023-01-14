#!/usr/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/string_utils.sh
source $THIS_DIR/log.sh

function exec_and_log()
{
    local log_file=$(fname_date_and_time)
	log_file="$log_file.txt"
	log "Log into: $log_file"
    local command_result=$($1)
	#[ -z $2 ] && dont_print=false || ($2 == false && dont_print=false || dont_printtrue))
	if [ -z $2 ]; then
		dont_print=false
	else
		if [ $2 == false ]; then
			dont_print=false
		else
			dont_print=true
		fi
	fi
	if ! $dont_print ; then
		echo $command_result
	fi
    echo $command_result >> $log_file
}

