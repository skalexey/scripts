#!/bin/bash

git_pull_job()
{
	source automation_config.sh
	local includes=("$scripts_dir/include/git_utils.sh")
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_pull_job]: "

	[ -z "$1" ] && log "No directory specified" && exit || log "do the job for '$1'"

	source git_utils.sh
	git_pull $1
}

job()
{
	git_pull_job $@
}
