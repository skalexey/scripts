#!/bin/bash

# deliver_build_scripts_job.sh

function deliver_config()
{
	[ ! -d "$1" ] && log_error "Not existent directory provided to deliver_config" && return 1 || local dir="$1"
	local ex=$2

	if [ ! -f "$dir/$ex.sh" ]; then
		log "Deliver new config '$dir/$ex'"
		cp "$scripts_dir/build_sh/${ex}_example.sh" "$dir/$ex.sh"
	else
		log "Config already exists '$dir/$ex.sh'"
	fi
}

function deliver_build_scripts_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
		"$scripts_dir/include/os.sh" \
		"$scripts_dir/include/input.sh" \
		"$scripts_dir/include/git_utils.sh" \
	)
	env_include ${includes[@]}
	source log.sh
	local log_prefix="[deliver_build_scripts_job]: "
	[ -z "$1" ] && log_error "No directory provided" && return 1 || dir="$1"
	[ ! -d "$dir" ] && log_error "Not existent directory provided: '$dir' relative to the invocation directory '${PWD}'" && return

	log "Deliver build scripts ..."

	local no_config=false
	if [ ! -z "$2" ] && [ "$2" == "no-config" ]; then
		log_info "'$2' option is passed. Will copy only main scripts"
		local no_config=true
	fi

	cp "$scripts_dir/build_sh/build.sh" "$dir"
	cp "$scripts_dir/build_sh/dependencies.sh" "$dir"
	cp "$scripts_dir/build_sh/get_dependencies.sh" "$dir"

	if ! $no_config; then
		deliver_config "$dir" build_config
		deliver_config "$dir" deps_config
		deliver_config "$dir" deps_scenario
		deliver_config "$dir" external_config
		[ $? -ne 0 ] && log_error "Error during build scripts delivery" && return 5
	fi

	cp "$scripts_dir/include/log.sh" "$dir"
	cp "$scripts_dir/include/os.sh" "$dir"
	cp "$scripts_dir/include/file_utils.sh" "$dir"
	[ $? -ne 0 ] && log_error "Error during build scripts delivery" && return 6

	file_replace "$dir/external_config.sh" "\{TPL_NAME\}" $(dir_name "$dir")

	log_success "Build scripts delivered"
	
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
	deliver_build_scripts_job $@
}
