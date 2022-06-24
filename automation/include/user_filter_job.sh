#!/bin/bash

# user_filter_job.sh

user_filter_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
		"$scripts_dir/include/os.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[user_filter_job]: "
	[ -z "$1" ] && log_error "Too few arguments 0 of 2" && exit
	[ -z "$2" ] && log_error "Too few arguments 1 of 2" && exit
}

job()
{
	user_filter_job $@
}
