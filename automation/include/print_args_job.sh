#!/bin/bash

# This is a handy job which can be used as a dummy for just checking the work of
# the parent job printing its output arguments
print_args_job()
{
	[ -z "$1" ] && exit || echo "[print_args_job]: '$@'"
}

job()
{
	print_args_job $@
}
