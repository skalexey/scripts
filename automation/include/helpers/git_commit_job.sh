#!/bin/bash

function git_commit_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/input.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_commit_job]: "

	[ -z "$1" ] && log_error "No directory provided" && return 1 || local dir="$1"

	cd "$dir"
	log_success '\nHit [Ctrl]+[D] to exit this child shell.'
	git status
	git add --patch
	exec bash
	exit
}

function job()
{
	git_commit_job $@
}
