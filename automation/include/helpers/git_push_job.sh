#!/bin/bash

function git_push_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/input.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_push_job]: "

	[ -z "$1" ] && log_error "No directory provided" && return 1 || eval local dir="$1"

	source git_utils.sh

	local tmp=${PWD}
	cd "$dir"

	git_pull
	git_push
	
	[ $? -ne 0 ] && log_error "Error during pushing" && cd "$tmp" && return 2
	
	cd "$tmp"
	
	return 0
}

function job()
{
	git_push_job $@
}
