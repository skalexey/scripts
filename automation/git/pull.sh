#!/bin/bash

function pull()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[pull]: "
	[ -z "$1" ] && log_error "No directory provided" && return 1 || eval local dir="$1"
	[ ! -d "$dir" ] && log_error "Not existent directory provided: '$dir'" && return 2

	source $THIS_DIR/../../include/file_utils.sh
	local dir_full_path=$(full_path "$dir")
    log "dir_full_path: $dir_full_path"
	$THIS_DIR/../run.sh \
		$automation_dir/include/helpers/git_pull_job.sh \
			"$dir_full_path"
	return 0
}

pull $@
[ $? -ne 0 ] && exit