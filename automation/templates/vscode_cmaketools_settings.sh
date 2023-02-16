#!/bin/bash

function vscode_cmaketools_settings()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../../include/file_utils.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[vscode_cmaketools_settings]: "
	[ -z "$1" ] && log_error "No target directory privided" && return 1 || local target_dir="$1"

	local proj_path="$(full_path "$target_dir")"
	~/Scripts/automation/run.sh ~/Scripts/automation/templates/vscode_cmaketools_settings_job.sh "$proj_path" ${@:2}
	[ $? -ne 0 ] && log_error "Error while calling vscode_cmaketools_settings.sh" && return 3
}

vscode_cmaketools_settings $@