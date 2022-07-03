#!/bin/bash

# This script runs any job passed as a script path forwarding all arguments to it
# Used in two cases:
# 	* to simplify run subjobs calls
#	* to run a job in a separated context (e.x. to be able to call new bash instance from it)

function run_local()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source "$THIS_DIR/log.sh"
	local log_prefix="[run_local]: "
	[ -z $1 ] && log_error "No job specified" && return 1 # job

	source "$THIS_DIR/file_utils.sh"
	if [ -z "$ENV_DIR" ]; then
		# Reconstruct the environment global variables and included objects
		source "$THIS_DIR/env.sh"
		source "$THIS_DIR/file_utils.sh"
		ENV_DIR=$(dir_full_path .)
		ENV_TARGET_DIR=$(dir_full_path ..)
	# else
		# log_info "Use environment '$ENV_DIR'"
	fi

	source "$1"
	
	source "$THIS_DIR/job.sh"
	local job=$(extract_job "$1")
	
	# call the job
	local jobname=$(extract_job_name "$job")
	$jobname ${@:2}

	return $?
}

run_local $@
