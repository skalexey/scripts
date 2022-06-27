#!/bin/bash

function git_check_stash_job()
{
	source automation_config.sh
	local includes=("$scripts_dir/include/git_utils.sh")
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_check_stash_job]: "

	[ -z "$1" ] && log_error "No directory specified" && exit

	source git_utils.sh
	if git_check_stash "$1"; then
		log_error "There are unprocessed stashes in '$1'"
	else
		log_success "All is ok in '$1'"
	fi
}

function job()
{
	git_check_stash_job $@
}
