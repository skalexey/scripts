#!/bin/bash

function create_backup() {
	source $THIS_DIR/config.sh
	local src=$1
	local destination=$2

	if [ -z "$destination" ]; then
		local current_date=$(date +'%Y-%m-%d')
		local current_time=$(date +'%H-%M-%S')
		local dir_name=$(basename "$src")
		local backup_dir="$backup_root/$current_date"
		local archive_name="$dir_name--$current_date--$current_time"
		local destination="$backup_dir/$archive_name"
	fi

	# Create backup directory if it doesn't exist
	mkdir -p "$backup_dir"

	# Create the archive
	source $scripts_dir/include/zip.sh
	compress "$src" "$destination"

	local code=$?
	[ $code -ne 0 ] && log_error "Failed to create backup (code: $code)" && return 1

	log_success "Backup created at '$destination'"
}

function job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/log.sh
	local this_script_name=$(basename "${BASH_SOURCE[0]}")
	local log_prefix="[$this_script_name] "

	
	[ -z "$1" ] && log_error "No source provided" && return 1 || local src="$1"
	create_backup "$src" "$2"
	local code=$?
	[ $code -ne 0 ] && log_error "Failed to create backup (code: $code)" && return 1
}


job $@
