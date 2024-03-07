#!/bin/bash

function cpp_cmake_project()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../../include/file_utils.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[cpp_cmake_project]: "
	[ -z "$1" ] && log_error "No project name provided" && return 1 || local project_name="$1"
	[ -z "$2" ] && log_error "No parent directory privided" && return 2 || local parent_dir="$2"

	local parent_dir_path="$(full_path "$parent_dir")"

    log_info "Create C++ CMake project '$project_name' in '$parent_dir_path'"

	~/Scripts/automation/run.sh ~/Scripts/automation/templates/cpp_cmake_project_job.sh "$project_name" "$parent_dir_path" ${@:3}
	[ $? -ne 0 ] && log_error "Error while calling cpp_cmake_project.sh" && return 3
}

cpp_cmake_project $@