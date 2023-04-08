#!/bin/bash

file_checksum_job()
{
	# Load environment with includes
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	local includes=(	"$scripts_dir/include/log.sh"
	)
	env_include ${includes[@]}
	# Init logger
	source log.sh
	local local_prefix="[$(basename "$0")]: "

	[ -z $1 ] && log_error "No file path specified" && return 1 || local fpath=$1
	# [ ! -f $fpath ] && log_error "Not existent file path provided" && return 2

	local base_name=$(basename "$fpath")
	if [ -f "$fpath" ]; then
		echo -e "\033[0;32m$base_name\033[0m": "$(shasum -a 256 "$fpath" | awk '{ print $1 }')"
	elif [ -d "$fpath" ]; then
		echo "Skip directory '$base_name'"
	else
		log_error "Not existent file path provided"
		return 2
	fi
}

job() 
{
	file_checksum_job $@
}
