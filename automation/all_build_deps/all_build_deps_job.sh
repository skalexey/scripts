#!/bin/bash

all_build_deps_job()
{
	source automation_config.sh
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/include/git_utils.sh"
						"$scripts_dir/automation/include" \
	)
	env_include ${includes[@]}

	local dir_list=(	"$projects_dir/vl_cpp_generator" \
						"$projects_dir/spellbook" \
						"$projects_dir/VL" \
						"$projects_dir/VL/JSONConverter" \
						"$projects_dir/DataModelBuilder/Core" \
	)

	[ -z $1 ] && echo "[all_build_deps]: No job specified" && exit || job=$1

	source list_job.sh

	list_job ${#dir_list[@]} ${dir_list[@]} $job ${@:2}
}

job() 
{
	all_build_deps_job $@
}
