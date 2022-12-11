#!/bin/bash

function stop()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"

	source ../../include/log.sh
	local log_prefix="[stop script]: "

	log_info "Stop the server..."
	source perforce_config.sh

	p4 -p $perforce_port admin stop

	[ $? -ne 0 ] && log_error "Error while stopping the server" && return 1
	log_success "stopped"

	return 0
}

stop $@
