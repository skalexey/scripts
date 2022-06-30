#!/bin/bash

function git_check_update_job()
{
	source automation_config.sh
	local def_job1="$automation_dir/include/helpers/print_updates_job.sh"
	local includes=("$scripts_dir/include/git_utils.sh" "$def_job1")
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_check_update_job]: "

	[ -z "$1" ] && log_error "No directory specified" && return 1 || local dir="$1"
	[ -z "$2" ] && local job1_path="$def_job1" || local job1_path="$2"
	[ ! -z "$3" ] && local job2_path="$3" || local job2_path="$def_job1"

	source git_utils.sh
	source job.sh

	log_info "Check update in '$dir'"

	git_check_update_ret=$(git_check_update "$dir")

	[ $? -ne 0 ] && log_error "Error during checking repo status" && return 2

	if [ "$git_check_update_ret" != "up_to_date" ]; then
		local job1=$(extract_job $job1_path)
		source $job1
		local job1_name=$(extract_job_name $job1)
		$job1_name "$1" "$git_check_update_ret" ${@:4}
	else
		if [ ! -z "$job2_path" ]; then
			local job2=$(extract_job $job2_path)
			source $job2
			local job2_name=$(extract_job_name $job2)
			$job2_name "$1" "$git_check_update_ret" ${@:4}
		fi
	fi
}

function print_updates()
{
	source log.sh
	local log_prefix="[git_check_update_job]: "
	if [ "$2" != "up_to_date" ]; then
		log_info "There are updates in '$1'"
	else
		log_success "Up-to-date '$1'"
	fi
}

function job()
{
	git_check_update_job $@
}
