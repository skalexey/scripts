#!/bin/bash

function cmake_modules_check_job()
{
	source automation_config.sh
	local def_job1="$automation_dir/include/helpers/print_cmake_modules_check_status_job.sh"
	local includes=(
		"$def_job1" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[cmake_modules_check_job]: "

	[ -z "$1" ] && log "No directory specified" && return 1 || local dir="$1"
	[ -z "$2" ] && local job1_path="$def_job1" || local job1_path="$2"
	[ -z "$3" ] && local job2_path="$def_job1" || local job2_path="$3"

	[ ! -d "$dir" ] && log_error "Not existent directory passed: '$dir'" && return 2

	log_info "Check status in '$dir'"

	if check_status $@; then
		source run_local.sh "$job1_path" "$1" "contains" ${@:4}
	else
		if [ ! -z "$job2_path" ]; then
			source run_local.sh "$job2_path" "$1" "negative" ${@:4}
		fi
	fi

	return 0
}

function check_status()
{
	if [ -f "$1/update_cmake_modules.sh" ]; then
		return 0
	else
		return 1
	fi
}

function print_status()
{
	source log.sh
	local log_prefix="[cmake_modules_check_job]: "
	if check_status $1; then
		log_success "Contains update_cmake_modules.sh"
		local list=$(find $1 -type d -name cmake_modules)
		for cmake_modules_dir in $list; do
			local subdir=$(dirname $cmake_modules_dir)
			log "  Modules exist in '$subdir'"
		done
	else
		log_warning "No update_cmake_modules.sh"
	fi
}

function job()
{
	cmake_modules_check_job $@
}
