#!/bin/bash

all_subprojects_job()
{
	# Load environment with includes
	source automation_config.sh
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/os.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/automation/include" \
						"$automation_dir/cpptests/cpptests_config.sh" \
	)
	env_include ${includes[@]}
	# Init logger
	source log.sh
	local local_prefix="[all_subprojects_job]: "

	project_dir=$2
	[ ! -d "$project_dir" ] && log_error "Project dir provided is invalid ('$project_dir')" && exit

	# Create directory list
	local dir_list=()
	for d in $project_dir/*/ ; do
		[ -f "$d/CMakeLists.txt" ] && dir_list+=($d) || log "Skip directory '$d' (not a subproject)"
	done
	#echo ${dir_list[@]}

	[ -z $1 ] && log_error "No job specified" && exit || job=$1

	source list_job.sh

	list_job ${#dir_list[@]} ${dir_list[@]} $job ${@:2}
}

job() 
{
	all_subprojects_job $@
}
