#!/bin/bash

# deliver_build_scripts_job.sh

function deliver_build_scripts_job()
{
	source automation_config.sh
	local includes=(
		"$scripts_dir/include/file_utils.sh" \
		"$scripts_dir/include/file_utils.py" \
		"$scripts_dir/include/os.sh" \
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

	if $no_config; then
		cp "$scripts_dir/build_sh/build.sh" "$dir"
		cp "$scripts_dir/build_sh/dependencies.sh" "$dir"
		cp "$scripts_dir/build_sh/get_dependencies.sh" "$dir"
	else
		cp -a "$scripts_dir/build_sh/." "$dir"
		rename "$dir/build_config_example.sh" build_config.sh
		rename "$dir/external_config_example.sh" external_config.sh
		rename "$dir/deps_config_example.sh" deps_config.sh
		rename "$dir/deps_scenario_example.sh" deps_scenario.sh
		[ $? -ne 0 ] && log_error "Error during build scripts delivery" && return 5
	fi

	cp "$scripts_dir/include/log.sh" "$dir"
	cp "$scripts_dir/include/os.sh" "$dir"
	cp "$scripts_dir/include/file_utils.sh" "$dir"
	[ $? -ne 0 ] && log_error "Error during build scripts delivery" && return 6

	file_replace "$dir/external_config.sh" "\{TPL_NAME\}" $(dir_name "$dir")

	log_success "Buld scripts delivered"
}

function job()
{
	deliver_build_scripts_job $@
}
