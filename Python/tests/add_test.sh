#!/usr/bin/bash

function job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd $THIS_DIR
	source automation_config.sh
	source $scripts_dir/include/log.sh
	source $scripts_dir/include/file_utils.sh
	THIS_FNAME=$(basename "${BASH_SOURCE[0]}")
	local log_prefix="[$THIS_FNAME]: "
	[ -z "$1" ] && log_error "No test name provided" && return 1 || local test_name="$1"
	fpath=${test_name}_test.py
	title=$(echo "$test_name" | tr '_' ' ' | sed -r 's/\b[a-z]/\U&/g')
	log_info "Creating test '$title' in '$fpath'"
	[ -f "$fpath" ] && log_error "Test file '$fpath' already exists" && return 2
	cp test_template.py $fpath
	[ $? -ne 0 ] && log_error "Error while copying test template" && return 2
	file_replace "$fpath" "{NAME}" "$test_name"
	file_replace "$fpath" "{TITLE}" "$title"
	[ $? -ne 0 ] && log_error "Error while replacing test template" && return 3
}

job $@
