#!/bin/bash

# This is a handy job which can be used as a dummy for just checking the work of
# the parent job printing its output arguments
print_args_job()
{
	[ -z "$1" ] && exit || echo -e "\033[0;33m[print_args_job]\033[0m: \033[0;32m'$@'\033[0m"
}

job()
{
	print_args_job $@
}
