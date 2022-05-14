#!/bin/bash

all_build_deps_job()
{
	ai="automation/include"
	si="include"
	includes=(	"$si/log.sh" \
				"$si/file_utils.sh" \
				"$si/file_utils.py" \
				"automation/automation_config.sh" \
				"$ai/dir_job.sh" \
				"$ai/dir_file_job.sh" \
				"$ai/list_job.sh" \
				"$ai/print_args_job.sh" \
	)
	env_include ${includes[@]}

	source automation_config.sh

	dir_list=(	"$projects_dir/vl_cpp_generator" \
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
