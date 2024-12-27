#!/bin/bash

all_build_scripts_job()
{
	source automation_config.sh
	
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/os.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/automation/include" \
	)
	env_include ${includes[@]}

	local dir="$scripts_dir/build_sh"

	[ -z $1 ] && echo "[all_build_scripts_job]: No job specified" && exit || job=$1

	source list_job.sh

	list_job ${#dir_list[@]} ${dir_list[@]} $job ${@:2}
}

job() 
{
	all_build_deps_job $@
}
