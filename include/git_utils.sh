#!/bin/bash

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/log.sh"

function git_check_stash()
{
	source log.sh
	local log_prefix="[git_check_stash]: "

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		local path=$1
		local cur_dir=${PWD}
		cd "$path"
	fi
	res=false
	local stash_marker="git_utils.sh script stash"
	local stash_list_res=$(git stash list | grep "$stash_marker")
	if [ ! -z "$stash_list_res" ]; then
		res=true
	fi
	
	[ ! -z cur_dir ] && cd "$cur_dir"
	
	$res
}

function git_untracked_list()
{
	git ls-files --others --exclude-standard
}

function git_push()
{
	local branch=$(git_get_current_branch)
	[ $? -ne 0 ] && log_error "Error during the current branch retrieving" &&  return 1
	git push origin $branch
	return $?
}

function git_pull()
{
	source log.sh
	local log_prefix="[git_pull]: "

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		local path=$1
		local cur_dir=${PWD}
		cd "$path"
	fi

	local status_res=$(git status | grep "Changes not staged for commit")
	local stash_marker="git_utils.sh script stash"
	if [ ! -z "$status_res" ]; then
		log_info "Stash the local work"
		git stash save "$stash_marker"
		[ $? -eq 0 ] && log "Stashed" || (log_error "Error while stashing. Stop the job" && return 1)
	fi
	local branch=$(git_get_current_branch)
	log "Current branch: '$branch'"
	log "Pull command: git pull origin ${branch} --rebase"
	git pull origin ${branch} --rebase

	if [ ! -z "$status_res" ]; then
		log_info "Pop back the local work"
		local stash_list_res=$(git stash list | grep "$stash_marker")
		if [ ! -z "$stash_list_res" ]; then
			git stash pop
		fi
	fi
	
	[ ! -z cur_dir ] && cd "$cur_dir"
}

function git_not_staged()
{
	local status_res=$(git status | grep "Changes not staged for commit")
	if [ ! -z "$status_res" ]; then
		true
	else
		false
	fi
}

function git_untracked()
{
	local status_res=$(git status | grep "Untracked files:")
	if [ ! -z "$status_res" ]; then
		true
	else
		false
	fi
}

function uncommitted_changes()
{
	if git_not_staged || git_untracked; then
		true
	else
		false
	fi
}

function need_to_commit()
{
	local status_res=$(git status | grep "Changes to be committed")
	if [ ! -z "$status_res" ]; then
		true
	else
		false
	fi
}

function git_check()
{
	source log.sh
	local log_prefix="[git_check]: "

	# arguments
	if [ ! -z $1 ]; then # directory path. If not provided then this directory is used
		cd "$1"
	fi

	# Deprecated:
	# [ "$2" == "verbose" ] && verbose=true

	if need_to_commit; then
		echo "need_to_commit"
		return 0
	fi

	if uncommitted_changes; then
		echo "uncommitted_changes"
		return 0
	fi

	local s=$(git_status false)
	
	[ $? -ne 0 ] && log_error "Error during checking repo status" && return 1

	if [ "$s" == "need_to_push" ]; then
		echo "$s"
		return 0
	fi

	echo "clean"
	return 0
}

function git_check_msg()
{
	[ -z "$1" ] && echo "No status provided" && return 1

	if [ "$1" == "clean" ]; then
		echo "Clean"
	elif [ "$1" == "need_to_commit" ]; then
		echo "Need to commit"
	elif [ "$1" == "uncommitted_changes" ]; then
		echo "Uncommitted changes"
	else
		echo $(git_status_msg "$1")
	fi

	return 0
}

function git_get_current_branch()
{
	echo $(git rev-parse --abbrev-ref HEAD)
}

function git_get_upstream()
{
	local ret="$(git rev-parse --abbrev-ref --symbolic-full-name "@{u}" 2>/dev/null)"
	[ -z "$ret" ] && ret="origin/$(git_get_current_branch)"
	echo "$ret"
}

function need_to_push()
{
	[ "$(git_status false)" == "need_to_push" ] && true || false 
}

function git_status()
{
	if [ -z "$1" ] || $1; then
		git fetch
	fi

	local upstream="$(git_get_upstream)"
	[ -z "$upstream" ] && upstream="origin/$(git_get_current_branch)"
	local local_b=$(git rev-parse @)
	local remote=$(git rev-parse "$upstream")
	local base=$(git merge-base @ "$upstream")

	# echo "upstream: '$upstream'"
	# echo "local_b: '$local_b'"
	# echo "remote: '$remote'"
	# echo "base: '$base'"

	ret="unknown"
	if [ "$local_b" = "$remote" ]; then
		ret="up_to_date"
	elif [ "$local_b" = "$base" ]; then
		ret="need_to_pull"
	elif [ "$remote" = "$base" ]; then
		ret="need_to_push"
	else
		ret="diverged"
	fi

	[ ! -z "$cur_dir" ] && cd "$cur_dir"

	echo "$ret"
}

function git_status_msg()
{
	[ -z "$1" ] && echo "No status provided" && return 1

	if [ "$1" == "up_to_date" ]; then
		echo "Up-to-date"
	elif [ "$1" == "need_to_pull" ]; then
		echo "Need to pull"
	elif [ "$1" == "need_to_push" ]; then
		echo "Need to push"
	else
		echo "Unknown status '$1'"
	fi

	return 0
}

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

	echo "$(git_status)"

	return 0
}

function git_ask_add_untracked_files()
{
	source input.sh
	if git_untracked; then
		local list=$(git_untracked_list)
		for e in ${list[@]}; do
			if ask_user "Add '$e' ?"; then
				git add "$e"
			fi
		done
	fi
}

function git_commit()
{
	git commit -m "$*"
}

function git_add_patch()
{
	git add --patch
}

if [ "$#" -gt 0 ]; then
	$@
fi