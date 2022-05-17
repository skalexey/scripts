#!/bin/bash

# This job simply calls cp $1 $2 on the given two arguments

copy_job()
{
	source log.sh
	log_prefix="[copy_job]: "
	[ -z "$1" ] && log_error "too few arguments 0 of 2" && exit
	[ -z "$2" ] && log_error "too few arguments 1 of 2" && exit
	cp "$1" "$2"
	[ $? -ne 0 ] && log_error "error for command cp \"$1\" \"$2\"" || log_success "command done: cp \"$1\" \"$2\""
}

job()
{
	copy_job $@
}
