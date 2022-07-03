#!/bin/bash

function ask_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/input.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[ask_job]: "

	[ -z "$1" ] && log_error "No data provided" && return 1 || local data="$1"
	[ -z "$2" ] && log_error "No question provided" && return 2 || local question="$2"
	[ -z "$3" ] && log_error "No job provided" && return 3 || local job_path="$3"

	[ ! -f "$job_path" ] && log_error "Not existent job provided: '$job_path'"

	source input.sh

	if ask_user "$question"; then
		./run_local.sh "$job_path" "$data"
	fi
}

function job()
{
	ask_job $@
}
