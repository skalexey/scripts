#!/bin/bash

git_check_job()
{
	source automation_config.sh
	local includes=("$scripts_dir/include/git_utils.sh")
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_check_job]: "

	[ -z "$1" ] && log "No directory specified" && exit

	source git_utils.sh
	git_check $1 $2
}

job()
{
	git_check_job $@
}
