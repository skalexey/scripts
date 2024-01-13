#!/bin/bash

function print_cmake_modules_check_status_job()
{
	source cmake_modules_check_job.sh
	print_status $@
}

function job()
{
	print_cmake_modules_check_status_job $@
}
