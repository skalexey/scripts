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

	[ -z "$1" ] && log_error "No directory provided" && return 1 || local dir="$1"
	local tmp=${PWD}
	cd "$dir"
	source git_utils.sh
	local branch=$(git_get_current_branch)
	[ $? -ne 0 ] && log_error "Error during the current branch retrieving" && cd "$tmp" &&  return 2

	git push origin $branch
	[ $? -ne 0 ] && log_error "Error during pushing" && cd "$tmp" && return 3
	
	cd "$tmp"
	
	return 0
}

function job()
{
	git_push_job $@
}
