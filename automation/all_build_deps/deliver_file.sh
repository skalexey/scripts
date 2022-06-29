#!/bin/bash

function deliver_file()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[deliver_file]: "
	[ -z "$1" ] && log_error "No file path provided" && return 1 || local fpath="$1"
	[ ! -f "$fpath" ] && log_error "Not existent file provided: '$fpath'" && return 2

	source $THIS_DIR/../../include/file_utils.sh
	local ffullpath=$(full_path "$fpath")
    log "ffullpath: $ffullpath"
	$THIS_DIR/../run.sh \
		$THIS_DIR/all_build_deps_job.sh \
			$THIS_DIR/../include/swap_args_job.sh \
			"$ffullpath" \
			$THIS_DIR/../include/print_args_job.sh
	return 0
}

deliver_file $@
[ $? -ne 0 ] && exit