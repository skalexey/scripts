#!/bin/bash

all_build_files_dir_job()
{
	ai="automation/include"
	si="include"
	includes=(	"$si/log.sh" \
				"$si/file_utils.sh" \
				"$si/file_utils.py" \
				"automation/automation_config.sh" \
				"$ai/dir_job.sh" \
				"$ai/dir_file_job.sh" \
				"$ai/print_args_job.sh" \
	)
	env_include ${includes[@]}

	source automation_config.sh

	file_list=(	build.sh \
				dependencies.sh \
				get_dependencies.sh \
				deps_scenario.sh \
				build_utils.sh \
	)

	[ -z $1 ] && echo "[all_build_files]: No directory specified" && exit || input_dir=$1
	[ -z $2 ] && echo "[all_build_files]: No job specified" && exit || job=$2

	source dir_job.sh

	dir_job $input_dir ${#file_list[@]} ${file_list[@]} $job ${@:3}
}

job()
{
	all_build_files_dir_job $@
}
