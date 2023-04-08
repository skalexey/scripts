#!/bin/bash

# dir_file_list_job.sh

function dir_file_list_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[$(basename "$0")]: "
	[ -z $1 ] && log_error "No directory specified" && return 1 || dir=$1
	[ -z $2 ] && log_error "No job specified" && return 2 || job=$2

	[ ! -d "$dir" ] && log_error "Not existent directory path provided '$dir'" && return 3
	if [ ! -z $3 ]; then
		local prefix="$dir/"
	fi

	# Read a list from the file
	local list=()
	local lines="$(ls "$dir" -1)"
	for line in $lines; do
		list+=("$prefix$line")
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
	dir_file_list_job $@
}
