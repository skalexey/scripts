#!/bin/bash

function update_cmake_modules_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/input.sh" \
		"$automation_dir/include/helpers/ask_job.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[update_cmake_modules_job]: "

	[ -z "$1" ] && log_error "No directory provided" && return 1 || local dir="$1"

	source input.sh
	source cmake_modules_check_job.sh
	print_status $@

	if [ "$2" == "contains" ]; then
		# source ask_job.sh
		# ask_job "$dir" "Update?" update_cmake_modules_job.sh
		log_info "Updating..."
		# No directory provided. Check for every subdirectory that contains cmake_modules folder
		local list=$(find $dir -type d -name cmake_modules)
		for cmake_modules_dir in $list; do
			local subdir=$(dirname $cmake_modules_dir)
			log_info "Updating '$subdir'..."
			$dir/update_cmake_modules.sh "$subdir"
			local retcode=$?
			[ $retcode -ne 0 ] && log_error "Failed to update '$dir'" && return 2 || log_success "Done with '$dir'"
		done
	elif [ "$2" == "negative" ]; then
		log "Nothing to update"
	fi
}

function job()
{
	update_cmake_modules_job $@
}
