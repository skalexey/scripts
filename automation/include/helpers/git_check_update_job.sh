#!/bin/bash

function git_check_update_job()
{
	source automation_config.sh
	def_job1="$automation_dir/include/helpers/print_updates_job.sh"
	local includes=("$scripts_dir/include/git_utils.sh" "$def_job1")
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_check_update_job]: "

	[ -z "$1" ] && log_error "No directory specified" && exit || dir=$1
	[ -z "$2" ] && job1_path=$def_job1 || job1_path=$2
	[ ! -z "$3" ] && job2_path=$3

	source git_utils.sh
	source job.sh

	if git_check_update $dir; then
		job1=$(extract_job $job1_path)
		source $job1
		job1_name=$(extract_job_name $job1)
		log_warning "job1_name: '$job1_name'"
		log_warning "args: ${@:4}"
		$job1_name "$1" ${@:4}
	else
		if [ ! -z "$job2_path" ]; then
			job2_name=$(extract_job_name $job2)
			log_warning "job2_name: '$job2_name'"
			log_warning "args: ${@:3}"
			$job2_name "$1" ${@:4}
		fi
	fi
}

function print_updates()
{
	source log.sh
	local log_prefix="[git_check_update_job]: "
	if $2; then
		log "there are updates in '$1'"
	else
		log "no updates in '$1'"
	fi
}

function job()
{
	git_check_update_job $@
}
