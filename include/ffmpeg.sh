#!/usr/bin/bash

function make_gif() {
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation/automation_config.sh
	source $scripts_dir/include/log.sh
	local log_prefix="[make_gif]: "
	[ -z "$1" ] && log_error "No input file provided" && return 1 || local input_file_resolved=$(eval echo "$1") && echo "input_file_resolved: "$input_file_resolved""
	[ -z "$2" ] && log_error "No output file provided" && return 1 || local output_file_resolved=$(eval echo "$2")
	[ -z "$3" ] && log_error "No fps provided" && return 1 || local fps=$3
	[ ! -z "$4" ] && local dimensions=$4
	local filter_additions=""
	[ ! -z "$dimensions" ] && filter_additions="$filter_additions,scale=$dimensions"
	# Validate scale argument (must be a positive integer)
	local cmd="ffmpeg -i \"$input_file_resolved\" -vf "fps=$fps$filter_additions" -y \"$output_file_resolved\""
	log_info "Executing: $cmd"
	eval "$cmd"
}

function extract_frame() {
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation/automation_config.sh
	source $scripts_dir/include/log.sh
	local log_prefix="[extract_frame]: "
	[ -z "$1" ] && log_error "No input file provided" && return 1 || local input_file_resolved=$(eval echo "$1")
	[ -z "$2" ] && log_error "No output file provided" && return 1 || local output_file_resolved=$(eval echo "$2")
	[ -z "$3" ] && log_error "No time provided" && return 1 || local time=$3
	local cmd="ffmpeg -i \"$input_file_resolved\" -ss $time -vframes 1 -y \"$output_file_resolved\""
	log_info "Executing: $cmd"
	eval "$cmd"
}

