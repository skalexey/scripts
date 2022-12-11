#!/bin/bash

function stop()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"

	source perforce_config.sh
	
	source ../../include/log.sh
	local log_prefix="[start script]: "

	log_info "Start the Perforce server on port '$perforce_port'"
	
	p4d -r "$perforce_dir" -d -p $perforce_port
	
	[ $? -ne 0 ] && log_error "Error while starting the server" && return 1
	
	log_success "Server started"

	return 0
}

stop $@
