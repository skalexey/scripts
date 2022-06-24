#!/bin/bash

function print_updates_job()
{
	source git_check_update_job.sh
	print_updates $@
}

function job()
{
	print_updates_job $@
}
