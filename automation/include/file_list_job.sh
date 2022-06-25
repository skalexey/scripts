#!/bin/bash

# file_list_job.sh

function file_list_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[file_list_job]: "
	[ -z $1 ] && log_error "No file path specified" && return 1 || fpath=$1
	[ -z $2 ] && log_error "No job specified" && return 2 || job=$2

	[ ! -f "$fpath" ] && log_error "Not existent file path provided '$fpath'" && return 3


	# Read a list from the file
	local list=()
	local lines="$(cat "$fpath")"
	for line in $lines; do
		local list+=("$line")
	done

	# Run list_job
	source list_job.sh
	local tmp=$list_job_log
	list_job_log=false
	list_job ${#list[@]} ${list[@]} $job ${@:3}
	list_job_log=$tmp

	return 0
}

function job()
{
	file_list_job $@
}
