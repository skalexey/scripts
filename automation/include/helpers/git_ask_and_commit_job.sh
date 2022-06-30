#!/bin/bash

function git_ask_and_commit_job()
{
	source automation_config.sh
	local includes=(
		"$automation_dir/include/helpers/git_ask_and_commit_or_push_job.sh" \
	)
	
	source git_ask_and_commit_or_push_job.sh
	local tmp=$only_commit
	local only_commit=true
	git_ask_and_commit_or_push_job $@
	only_commit=$tmp
}

function job()
{
	git_ask_and_commit_job $@
}
