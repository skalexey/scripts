#!/bin/bash

function print_git_check_status_job()
{
	source git_check_job.sh
	print_status $@
}

function job()
{
	print_git_check_status_job $@
}
