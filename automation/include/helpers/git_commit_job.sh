#!/bin/bash

function _cycle_()
{
	while : ; do
		if git_not_staged; then
			git add --patch
		fi

		if git_untracked; then
			local list=$(git_untracked_list)
			for e in ${list[@]}; do
				if ask_user "Add '$e' ?"; then
					git add "$e"
				fi
			done
		fi

		if need_to_commit; then
			if [ ! -z "$2" ]; then
				log_info "git commit -m \"$(echo "${@:2}")\""
				git commit -m "$(echo "${@:2}")"
			else
				if ask_user "Commit?"; then
					git commit
				fi
			fi
		fi

		if [ "$(git_status false)" == "need_to_push" ]; then
			if ask_user "Push?"; then
				git_push
			fi
		fi

		if uncommitted_changes || need_to_commit || [ "$(git_status false)" == "need_to_push" ]; then
			if ! ask_user "Something else?"; then
				break
			fi
		else
			break
	    fi
	done
}

function git_commit_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/input.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[git_commit_job]: "

	[ -z "$1" ] && log_error "No directory provided" && return 1 || local dir="$1"

	source git_utils.sh
	source input.sh
	local cur_dir="${PWD}"
	cd "$dir"
	log_success '\nHit [Ctrl]+[D] to exit this child shell.'
	git status

	_cycle_

	exec bash
	exit
}

function job()
{
	git_commit_job $@
}
