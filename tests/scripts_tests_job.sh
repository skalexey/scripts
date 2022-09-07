#!/bin/bash

function scripts_tests_job()
{
	env_include "$scripts_dir/include/net_utils.sh"
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"
	[ ! -d tmp ] && mkdir tmp
	local folder_name=${PWD##*/}
	local log_prefix="-- [${folder_name}]: "
	source tests.sh
}

function job()
{
	scripts_tests_job $@
}