#!/bin/bash

function git_ask_and_commit_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/input.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_ask_and_commit_job]: "

	[ -z "$1" ] && log_error "No directory provided" && return 1 || local dir="$1"

	source input.sh
	source git_check_job.sh
	print_status $@

	if $2; then
		if ask_user "Commit?"; then
			cd "$dir"
			log_success '\nHit [Ctrl]+[D] to exit this child shell.'
			git status
			git add --patch
			exec bash
			exit
		fi
	fi
}

function job()
{
	git_ask_and_commit_job $@
}
