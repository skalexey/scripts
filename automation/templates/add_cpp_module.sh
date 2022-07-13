#!/bin/bash

function add_cpp_module()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../../include/file_utils.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[add_cpp_module]: "
	[ -z "$1" ] && log_error "No module name provided" && return 1 || local module_name="$1"
	[ -z "$2" ] && log_error "No target directory privided" && return 2 || local target_dir="$2"

	local subproj_path="$(full_path "$target_dir")"
	~/Scripts/automation/run.sh ~/Scripts/automation/templates/cpp_module_job.sh "$module_name" "$subproj_path" ${@:2}
	[ $? -ne 0 ] && log_error "Error while calling cpp_modue_job.sh" && return 3
}

add_cpp_module $@