#!/bin/bash

function git_pull_job()
{
	source automation_config.sh
	local includes=("$scripts_dir/include/git_utils.sh")
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_pull_job]: "

	[ -z "$1" ] && log_error "No directory specified" && exit || log "Do the job for '$1'"

	source git_utils.sh
	git_pull $1
}

function job()
{
	git_pull_job $@
}
