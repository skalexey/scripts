#!/bin/bash

function create_from_template()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/file_utils.sh
	source $scripts_dir/include/log.sh
	THIS_FNAME=$(basename "${BASH_SOURCE[0]}")
	local log_prefix="[$THIS_FNAME]: "
	[ -z "$1" ] && log_error "No file name provided" && return 1 || local file_name="$1"
	[ -z "$2" ] && log_error "No target directory privided" && return 2 || local target_dir="$2"

	local subproj_path="$(full_path "$target_dir")"
	$scripts_dir/automation/run.sh $scripts_dir/automation/templates/create_from_template_job.sh "$file_name" "$subproj_path" ${@:2}
	[ $? -ne 0 ] && log_error "Error while calling create_from_template_job.sh" && return 3
}

create_from_template $@