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
	[ ! -d "$dir" ] && log_error "Not existent directory provided: '$dir' relative to the invocation directory '${PWD}'" && exit

	log "Deliver build scripts ..."

	cp -a "$scripts_dir/build_sh/." "$dir"
	cp "$scripts_dir/include/log.sh" "$dir"
	cp "$scripts_dir/include/os.sh" "$dir"
	cp "$scripts_dir/include/file_utils.sh" "$dir"

	[ $? -ne 0 ] && log_error "Error during build scripts delivery: $?" && exit 5
	rename $dir/build_config_example.sh build_config.sh
	rename $dir/deps_config_example.sh deps_config.sh
	rename $dir/deps_scenario_example.sh deps_scenario.sh
	[ $? -ne 0 ] && log_error "Error during build scripts delivery: $?" && exit 5

	log_success "Buld scripts delivered"
}

function job()
{
	deliver_build_scripts_job $@
}
