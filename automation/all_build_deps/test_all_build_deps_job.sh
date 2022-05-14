#!/bin/bash

test_all_build_deps_job()
{
	# load dependencies to the env directory
	local ai="automation/include"
	local si="include"
	local includes=(	"$si/log.sh" \
				"$si/file_utils.sh" \
				"$si/file_utils.py" \
				"automation/automation_config.sh" \
				"$ai/dir_job.sh" \
				"$ai/dir_file_job.sh" \
				"$ai/list_job.sh" \
				"$ai/print_args_job.sh" \
				"$ai/copy_job.sh" \
	)
	env_include ${includes[@]}

	# configuration
	local test_dir_list=(	"vl_cpp_generator1" \
							"vl_cpp_generator2" \
	)

	source automation_config.sh

	local take_dir_list=(	"$projects_dir/vl_cpp_generator" \
							"$projects_dir/spellbook" \
	)

	# copy release files into the env directory
	source setup_test_environment.sh
	echo " --- Test environment is ready ---"

	[ -z $1 ] && echo "[test_all_build_deps_job]: No job specified" && exit || job=$1

	# do the job on test files located in the env directory
	source list_job.sh
	list_job ${#test_dir_list[@]} ${test_dir_list[@]} $job ${@:2}
}

job() 
{
	test_all_build_deps_job $@
}