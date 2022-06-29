#!/bin/bash

function all_build_deps_job()
{
	source automation_config.sh
	source "$automation_dir/cpptests/cpptests_config.sh"
	local cpptests_dir=$project_dir
	source "$automation_dir/util_tools/util_tools_config.sh"
	local util_tools_dir=$project_dir
	source "$automation_dir/nutrition_calculator/nutrition_calculator_config.sh"
	local nutrition_calculator_dir=$project_dir
	
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/include/git_utils.sh" \
						"$scripts_dir/automation/include" \
						"$automation_dir/include/list_job.sh" \
	)
	env_include ${includes[@]}

	local dir_list=(	"$projects_dir/vl_cpp_generator" \
						"$projects_dir/spellbook" \
						"$projects_dir/VL" \
						"$projects_dir/VL/JSONConverter" \
						"$projects_dir/DataModelBuilder/Core" \
						"$projects_dir/DataModelBuilder/Core" \
						"$cpptests_dir" \
						"$util_tools_dir" \
						"$nutrition_calculator_dir" \
						
	)

	[ -z $1 ] && echo "[all_build_deps]: No job specified" && exit || job=$1

	source list_job.sh

	list_job ${#dir_list[@]} ${dir_list[@]} $job ${@:2}
}

function job() 
{
	all_build_deps_job $@
}
