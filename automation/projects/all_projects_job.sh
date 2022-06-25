#!/bin/bash

all_projects_job()
{
	# Load environment with includes
	source automation_config.sh
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/os.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/automation/include"
	)
	env_include ${includes[@]}
	source projects_config.sh
	# Init logger
	source log.sh
	local local_prefix="[all_projects_job]: "

	# Create directory list
	local project_list_projects=()

	for d in $projects_dir/*/; do
		local dd=${d%/}
		[ ! -d "$dd/.git" ] && log "Skip dir '$d' (not a git repo)" || project_list_projects+=("$dd")
	done

	local dir_list=()
	dir_list+=("${project_list_stuff[@]}")
	# log "dir_list:"
	# echo "${dir_list[@]}"
	for e in ${project_list_projects[@]}; do
		if [[ ! "${dir_list[*]}" =~ "${e}" ]]; then
			dir_list+=("$e");
		# else
			# log_info "duplicate found: $e";
		fi
	done

	#echo ${project_list[@]}

	[ -z $1 ] && log_error "No job specified" && return 1 || local job=$1

	source list_job.sh
	local tmp=$list_job_log
	list_job_log=false
	list_job ${#dir_list[@]} ${dir_list[@]} $job ${@:2}
	list_job_log=$tmp

	return 0
}

job() 
{
	all_projects_job $@
}
