#!/bin/bash

function tmp_config()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/os.sh
	if is_mac; then
		project_dir=${HOME}/Projects/tmp
	else
		project_dir=${HOME}/Projects/tmp
	fi
}

tmp_config $@
