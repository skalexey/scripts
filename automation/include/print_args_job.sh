#!/bin/bash

# This is a handy job which can be used as a dummy for just checking the work of
# the parent job printing its output arguments
print_args_job()
{
	source log.sh
	local log_prefix="\033[0;33m[print_args_job]\033[0m: "
	tmp=$@ # prevent from splitting the argument for the log function as list
	[ -z "$1" ] && exit || log "\033[0;32m'$tmp'\033[0m"
}

job()
{
	print_args_job $@
}
