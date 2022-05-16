#!/bin/bash

source file_utils.sh
source log.sh

close_overlappings_file_job()
{
	local log_prefix="[close_overlappings_file_job]: "

	[ -z "$1" ] && log "No file path specified" && exit || log "do the job for $1"

	local ret=$(file_search "$1" "folderName=\$lastFolderName")
	log "search folderName saving into '$1': '$ret'"
	if [[ $ret -eq -1 ]]; then
		log "Insert folder name saving into '$1'"
		local ret=$(file_search $1 "folderName=")
		echo "validation result: $ret"
		#[[ $ret -ne -1 ]] && log " +++ SHOLD INSERT +++" || log " ~~~ SHOLD NOT INSERT ~~~"
		if [ $(file_insert_before "$1" "folderName=" "\nlastFolderName=\$folderName\n") -ne -1 ] ; then
			log " === INSERTED === folder name saving"
			file_append_line "$1" "folderName=\$lastFolderName"
			[[ $ret -ne -1 ]] && log " +++ OK +++" || log " !!!!!!!! SHOULD NOT BE !!!!!!"
		else
			log " --- NOT INSERTED --- folder name saving"
		fi
		#fi
	else
		log "Already contains"
	fi

	local ret=$(file_search "$1" "log_prefix=\$last_log_prefix")
	log "search log saving in '$1' result: '$ret'"
	if [[ $ret -eq -1 ]]; then
		local ret=$(file_search $1 "log_prefix=")
		echo "validation result: $ret"
		#[[ $ret -ne -1 ]] && log " +++ SHOLD INSERT +++" || log " ~~~ SHOLD NOT INSERT ~~~"
		if [ $(file_insert_before "$1" "log_prefix=" "\nlast_log_prefix=\$log_prefix\n") -ne -1 ]; then
			log " === INSERTED === log saving"
			file_append_line "$1" "log_prefix=\$last_log_prefix"
			[[ $ret -ne -1 ]] && log " +++ OK +++" || log " !!!!!!!! SHOULD NOT BE !!!!!!"
		else
			log " --- NOT INSERTED --- log saving"
		fi
	else
		log "Already contains"
	fi
}

job()
{
	close_overlappings_file_job $@
}
