#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source "$scripts_dir/include/log.sh"
local_prefix="[$(basename "$0")]: "

[ -z $1 ] && log_error "No directory specified" && exit 1 || dir=$1

log_info "automation_dir: $automation_dir"

$THIS_DIR/../run.sh \
	$automation_dir/include/dir_file_list_job.sh \
		$dir \
		$automation_dir/include/file_checksum_job.sh \
		true
