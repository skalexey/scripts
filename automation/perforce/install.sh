#!/bin/bash

function install()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"

	source $THIS_DIR/../automation_config.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[install]: "
	[ ! -d "$1" ] && log_error "No downloaded directory provided" && return 1 || local dir="$1"

	local bin_dir=/usr/local/bin
	local perforce_dir=/usr/local/perforce

	# Move the p4d server and p4 CLI executables from the Downloads directory to the "$bin_dir" directory
	log_info "Install '$dir/p4d' and p4 to '$bin_dir'"
	sudo cp "$dir/p4d" "$bin_dir/p4d"
	sudo cp "$dir/p4" "$bin_dir/p4"

	[ $? -ne 0 ] && log_error "Can't put executables to the binary directory" && return 2

	
	log_info "Make both moved files executable"
	sudo chmod +x "$bin_dir"/p4*
	[ $? -ne 0 ] && log_error "Can't change access level of the binaries" && return 3

	log_info "Create a perforce server directory at '$perforce_dir'"
	sudo mkdir "$perforce_dir"
	[ $? -ne 0 ] && log_error "Can't create the perforce directory" && return 4

	log_info "Set the permissions on the perforce directory"
	sudo chown $USER:admin "$perforce_dir"
	[ $? -ne 0 ] && log_error "Can't set permissions on the perforce directory" && return 5

	log_info "Time to check both binaries to confirm they run  as expected"
	p4d -V
	p4 -V
	[ $? -ne 0 ] && log_warning "Can't run. Check permissions..." && ls -lah "$bin_dir"/p4* && return 6
	
	log_info "Start the Perforce server"
	p4d -r "$perforce_dir" -d -p 1666

	[ $? -ne 0 ] && log_error "Can't start the server" && return 7
	
	log_info "test the server"
	p4 -p localhost:1666 info
	[ $? -ne 0 ] && log_error "Can't test the server" && return 8

	log_success "Finished setting up"

	return 0
}

install $@
job_retcode=$?
[ $job_retcode -ne 0 ] && exit $job_retcode
