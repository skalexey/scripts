#!/bin/bash

# user_filter_job.sh

function user_filter_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
		"$scripts_dir/include/input.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[user_filter_job]: "
	[ -z "$1" ] && log_error "No data provided" && return 1 || local data="$1"
	[ -z "$2" ] && log_error "No output file path provided" && return 2 || local fpath="$2"

	local dir="$(dirname "$fpath")"
	[ ! -d "$dir" ] && log_error "Not existent directory of a given file passed: '$dir'" && return 3

	log "Will store filtered data into '$fpath'"

	log_info "Input data: '$data'"

	source input.sh

	if ask_user "Accept this?"; then
		echo "$data" >> "$fpath"
		log_success "Accepted"
	else
		log_warning "Rejected"
	fi

	return 0
}

function job()
{
	user_filter_job $@
}
