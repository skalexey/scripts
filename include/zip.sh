#!/bin/bash

function include() {
	source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$1"
}

include ../utility.sh
include log.sh


function compress() {
	local log_prefix="[compress]: "

	[ -z "$1" ] && log_error "No source" && return 1 || local src="$1"

	if command_exists 7z; then
		local extension="7z"
	else
		local extension="zip"
	fi
	[ -z "$2" ] && local destination="${src%.*}$extension" || local destination="$2.$extension"
	[ ! -d "$src" ] && [ ! -f "$src" ] && log_error "Source file '$src' doesn't exist" && return 1
	[ -f "$destination" ] && log_error "Destination file '$destination' already exists" && return 1
	
	log_info "Compressing '$src' to '$destination'"
	if [ "$extension" == "7z" ]; then
		local cmd="7z a ${@:3} \"$destination\" \"$src\"" # -r -ssw 
		echo "Executing: $cmd"
		eval $cmd
	elif command_exists zip; then
		zip -r ${@:3} "$destination" "$src"
	else
		log_error "Error: You must install 7z or zip."
		return 1
	fi
}
