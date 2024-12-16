#!/bin/bash

function copy_files_from_file_list()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/log.sh
	local log_prefix="[copy_files_from_file_list]: "

	[ -z "$1" ] && log_error "No file list provided" && return 1 || local file_list=$1
	[ -z "$2" ] && log_error "No destination directory provided" && return 2 || local destination_dir=$2

	# Fix Windows-style line endings and convert Windows paths to Unix-like paths
	local fixed_file_list="${file_list}_fixed"
	sed 's/\r$//' "$file_list" | sed 's|\\|/|g' | sed 's|^\([a-zA-Z]\):|/\L\1|' > "$fixed_file_list"

	# Ensure the destination directory exists
	mkdir -p "$destination_dir" || { log_error "Failed to create destination directory"; return 3; }

	# Copy files from the fixed list
	xargs -a "$fixed_file_list" -I{} cp "{}" "$destination_dir"

	# Clean up the temporary fixed file
	rm -f "$fixed_file_list"
}

copy_files_from_file_list "$@"
