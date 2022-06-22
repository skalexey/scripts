#!/bin/bash

function update_cmake_subproject_job()
{
	# Init logger
	source log.sh
	local log_prefix="[update_cmake_subproject_job]: "

	# Load project config
	source cpptests_config.sh

	## Do the job
	subproj_dir=$1
	subproj_name="$(basename "$subproj_dir")"
	[ ! -d "$subproj_dir" ] && log_error "Not existent subproject directory '$subproj_dir'" && exit

	# Copy template
	source $automation_dir/templates/templates_config.sh
	fname="CMakeLists.txt"
	local tpl_path=$templates_dir/CMake/ExeIncludable/$fname
	[ ! -f "$tpl_path" ] && log_error "No template found at '$tpl_path'" && exit
	cp "$tpl_path" "$subproj_dir"
	[ $? -ne 0 ] && log_error "Errors while copying template '$subproj_name'"

	# Modify template content
	file_path=$subproj_dir/$fname
	file_replace $file_path "ExeTitle" "$subproj_name"

	[ $? -eq 0 ] && log_success "Done with '$subproj_name'" || (log_error "Errors while replacing template content of '$subproj_name'" && exit)
}

function job()
{
	update_cmake_subproject_job $@
}
