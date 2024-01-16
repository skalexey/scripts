#!/bin/bash

function update_build_scripts()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"

	source ../../include/log.sh
	local log_prefix="[update_scripts]: "	
	source ../automation_config.sh
	[ ! -f "os.sh" ] && cp ../../include/os.sh . && local os_included=true
	source "$automation_dir/templates/templates_config.sh"
	if $os_included; then
		rm os.sh
	fi
	
	[ $? -ne 0 ] && log_error "Error while delivering files" && return 1

	$automation_dir/run.sh \
		"$automation_dir/all_build_deps/all_build_deps_job.sh" \
		"$automation_dir/build_sh/deliver_build_scripts_job.sh"

	[ $? -ne 0 ] && log_error "Error while delivering files" && return 2

	log_success "Done"
}

update_build_scripts $@