#!/bin/bash

test_all_build_deps_job()
{
	# load dependencies to the env directory
	source automation_config.sh
	
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/automation/automation_config.sh" \
						"$scripts_dir/automation/include" \
	)
	env_include ${includes[@]}

	# configuration
	local test_dir_list=(	"vl_cpp_generator1" \
							"vl_cpp_generator2" \
	)

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