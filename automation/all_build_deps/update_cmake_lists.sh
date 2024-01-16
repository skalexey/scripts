#!/bin/bash

function update_deps_scenario_custom()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"

	source ../../include/log.sh
	local log_prefix="[update_scripts]: "	
	source ../automation_config.sh
	
	[ $? -ne 0 ] && log_error "Error while delivering files" && return 1

	$automation_dir/run.sh \
		"$automation_dir/all_build_deps/all_build_deps_job.sh" \
		"$automation_dir/cmake_cpp/update_cmake_lists_job.sh"

	[ $? -ne 0 ] && log_error "Error while delivering files" && return 2

	log_success "Done"
}

update_deps_scenario_custom $@