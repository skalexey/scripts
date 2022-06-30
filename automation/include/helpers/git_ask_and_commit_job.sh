#!/bin/bash

function git_ask_and_commit_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/input.sh" \
		"$automation_dir/include/helpers/ask_job.sh" \
		"$automation_dir/include/helpers/git_commit_job.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_ask_and_commit_job]: "

	[ -z "$1" ] && log_error "No directory provided" && return 1 || local dir="$1"

	source input.sh
	source git_check_job.sh
	print_status $@

	if [ "$2" == "need_to_commit" ]; then
		source ask_job.sh
		ask_job "$dir" "Commit?" git_commit_job.sh
	elif [ "$2" == "need_to_push" ]; then
		source ask_job.sh
		ask_job "$dir" "Push?" git_push_job.sh
	fi
}

function job()
{
	git_ask_and_commit_job $@
}
