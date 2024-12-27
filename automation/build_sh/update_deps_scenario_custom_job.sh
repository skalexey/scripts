#!/bin/bash

# update_deps_scenario_custom_job.sh

function deliver_config()
{
	[ ! -d "$1" ] && log_error "Not existent directory provided to deliver_config" && return 1 || eval local dir="$1"
	local ex=$2

	if [ ! -f "$dir/$ex.sh" ]; then
		log "Deliver new config '$dir/$ex'"
		cp "$scripts_dir/build_sh/${ex}_example.sh" "$dir/$ex.sh"
	else
		log "Config already exists '$dir/$ex.sh'"
	fi
}

function update_deps_scenario_custom_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
		"$scripts_dir/include/os.sh" \
		"$scripts_dir/include/input.sh" \
		"$scripts_dir/include/git_utils.sh" \
		"$scripts_dir/include/net_utils.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[update_deps_scenario_custom_job]: "
	[ -z "$1" ] && log_error "No directory provided" && return 1 || dir="$1"
	[ ! -d "$dir" ] && log_error "Not existent directory provided: '$dir' relative to the invocation directory '${PWD}'" && return

	log "Update ..."

	# file_insert_after "$dir/deps_scenario.sh" "deps_scenario()\n{" "\n\t"'local THIS_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"'
	# file_insert_after "$dir/deps_scenario.sh" "source " "\$THIS_DIR/"

	# [ $? -ne 0 ] && log_error "Error while updating deps_scenario.sh in '$dir'" && return 1
	
	log_success "Done"
	
	# auto commit with user dialog
	source git_utils.sh
	source input.sh
	local cur_dir=${PWD}
	cd "$dir"
	git status
	git add *.sh --patch
	git status
	if need_to_commit; then
		if ask_user "Commit?"; then
			git commit -m "Auto update build scripts"
		fi
	fi
	if need_to_push; then
		if ask_user "Push?"; then
			git_push
		fi
	fi
	cd "$cur_dir"
}

function job()
{
	update_deps_scenario_custom_job $@
}
