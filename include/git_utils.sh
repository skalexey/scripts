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
		cd "$path"
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
	
	[ ! -z cur_dir ] && cd "$cur_dir"
}

function git_check()
{
	source log.sh
	local log_prefix="[git_check]: "

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		local path=$1
		local cur_dir=${PWD}
		cd "$path"
	fi

	verbose=false
	[ "$2" == "verbose" ] && verbose=true

	ret=false
	local status_res=$(git status | grep "Changes not staged for commit")
	if [ ! -z "$status_res" ]; then
		if $verbose; then
			log_info "uncommitted changes in '$path'"
		fi
		ret=true
	elif $verbose; then
		log "no changes in '$path'"
	fi
	
	[ ! -z cur_dir ] && cd "$cur_dir"

	$ret
}

git_check_update_log=false
function git_check_update()
{
	source log.sh
	local log_prefix="[git_check_update]: "

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		local path=$1
		local cur_dir=${PWD}
		cd "$path"
		[ $? -ne 0 ] && log_error "Problem with directory '$path'" && return 1
	fi

	if $git_check_update_log; then
		log_info "Check updates at '$path'"
	fi

	git fetch

	local UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null)"
	[ -z "$UPSTREAM" ] && UPSTREAM="origin/$(git branch --show-current)"
	local LOCAL=$(git rev-parse @)
	local REMOTE=$(git rev-parse "$UPSTREAM")
	local BASE=$(git merge-base @ "$UPSTREAM")

	# echo "UPSTREAM: '$UPSTREAM'"
	# echo "LOCAL: '$LOCAL'"
	# echo "REMOTE: '$REMOTE'"
	# echo "BASE: '$BASE'"

	ret=false
	if [ "$LOCAL" = "$REMOTE" ]; then
		if $git_check_update_log; then
			log_success "Up-to-date"
		fi
	elif [ "$LOCAL" = "$BASE" ]; then
		if $git_check_update_log; then
			log_info "Need to pull"
		fi
		ret=true
	elif [ "$REMOTE" = "$BASE" ]; then
		if $git_check_update_log; then
			log_info "Need to push"
		fi
	else
		if $git_check_update_log; then
			log_warning "Diverged"
		fi
	fi

	[ ! -z "$cur_dir" ] && cd "$cur_dir"

	$ret
}

