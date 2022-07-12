#!/bin/bash

function deliver_build_scripts()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source "$THIS_DIR/../automation_config.sh"
	source "$scripts_dir/include/file_utils.sh"
	dir=$(full_path "$1")
	"$automation_dir/run.sh" \
		"$automation_dir/build_sh/deliver_build_scripts_job.sh" \
			"$dir" \
			${@:2}
}

deliver_build_scripts $@
