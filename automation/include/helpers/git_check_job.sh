#!/bin/bash

function git_check_job()
{
	source automation_config.sh
	local def_job1="$automation_dir/include/helpers/print_git_check_status_job.sh"
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$def_job1" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_check_job]: "

	[ -z "$1" ] && log "No directory specified" && return 1 || local dir="$1"
	[ -z "$2" ] && local job1_path="$def_job1" || local job1_path="$2"
	[ -z "$3" ] && local job2_path="$def_job1" || local job2_path="$3"

	[ ! -d "$dir" ] && log_error "Not existent directory passed: '$dir'" && return 2

	source git_utils.sh

	log_info "Check status in '$dir'"

	local check_result=$(git_check $@)
	if [ "$check_result" == "need_to_commit" ] || \
		[ "$check_result" == "need_to_push" ] || \
		[ "$check_result" == "uncommitted_changes" ] \
	; then
		source run_local.sh "$job1_path" "$1" "$check_result" ${@:4}
	else
		if [ ! -z "$job2_path" ]; then
			source run_local.sh "$job2_path" "$1" "$check_result" ${@:4}
		fi
	fi

	return 0
}

function print_status()
{
	source log.sh
	source git_utils.sh
	local log_prefix="[git_check_job]: "
	if [ "$2" != "clean" ]; then
		log_info "$(git_check_msg "$2") in '$1'"
	else
		log_success "Clean in '$1'"
	fi
}

function job()
{
	git_check_job $@
}
