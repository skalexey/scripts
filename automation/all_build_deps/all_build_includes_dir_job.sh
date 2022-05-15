#!/bin/bash

all_build_includes_dir_job()
{
	source automation_config.sh
	
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/automation/automation_config.sh" \
						"$scripts_dir/automation/include" \
	)
	env_include ${includes[@]}

	local file_list=(	build.sh \
						dependencies.sh \
						get_dependencies.sh \
						build_utils.sh \
	)

	[ -z $1 ] && echo "[all_build_files]: No directory specified" && exit || input_dir=$1
	[ -z $2 ] && echo "[all_build_files]: No job specified" && exit || job=$2

	source dir_job.sh

	dir_job $input_dir ${#file_list[@]} ${file_list[@]} $job ${@:3}
}

job()
{
	all_build_includes_dir_job $@
}
