#!/bin/bash

function git_pull()
{
	source log.sh
	local log_prefix="\033[0;32m[git_pull]: "
	local log_postfix="\033[0m"

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		local path=$1
		local cur_dir=${PWD}
		cd $path
	fi

	local status_res=$(git status | grep "Changes not staged for commit")
	local stash_marker="git_utils.sh script stash"
	if [ ! -z $status_res ]; then
		log "Stash local work"
		git stash -m $stash_marker
	fi
	local branch=$(git branch --show-current)
	log "Current branch: '$branch'"
	log "Pull command: git pull origin ${branch} --rebase"
	git pull origin ${branch} --rebase

	if [ ! -z $status_res ]
	then
		log "Pop back the local work"
		stash_list_res=$(git stash list | grep $stash_marker)
		if [ ! -z $stash_list_res ]; then
			git stash pop
		fi
	fi
	
	[ ! -z cur_dir ] && cd $cur_dir
}

function git_check()
{
	source log.sh
	local log_prefix="[git_check]: "

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		local path=$1
		local cur_dir=${PWD}
		cd $path
	fi

	verbose=false
	[ "$2" == "verbose" ] && verbose=true

	local status_res=$(git status | grep "Changes not staged for commit")
	if [ ! -z "$status_res" ]; then
		log_info "uncommitted changes in '$path'"
	elif $verbose; then
		log "no changes"
	fi
	
	[ ! -z cur_dir ] && cd $cur_dir
}

