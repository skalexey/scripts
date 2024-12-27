#!/bin/bash

# This job simply calls cp $1 $2 on the given two arguments if $2 exists

function update_job()
{
	source log.sh
	local log_prefix="[update_job]: "
	[ -z "$1" ] && log_error "too few arguments 0 of 2" && exit
	[ -z "$2" ] && log_error "too few arguments 1 of 2" && exit
	# $2 can be a directory, or a file path. We need to check if the source file lies in the destination or not
	if [ -d "$2" ]; then
		local file_name=$(basename "$1")
		local dest_file="$2/$file_name"
	else
		local dest_file="$2"
	fi
	if [ ! -f "$dest_file" ]; then
		return 0  # file does not exist, nothing to update
	fi
	cp "$1" "$2"
	[ $? -ne 0 ] && log_error "error for command cp \"$1\" \"$2\"" || log_success "command done: cp \"$1\" \"$2\""
}

job()
{
	update_job $@
}
