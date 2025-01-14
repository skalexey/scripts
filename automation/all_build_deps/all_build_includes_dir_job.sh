#!/bin/bash

all_build_includes_dir_job()
{
	source log.sh
	local log_prefix="[all_build_includes_dir_job]: "
	source automation_config.sh
	
	local includes=(	"$scripts_dir/include/log.sh" \
						"$scripts_dir/include/os.sh" \
						"$scripts_dir/include/file_utils.sh" \
						"$scripts_dir/include/file_utils.py" \
						"$scripts_dir/automation/include" \
	)
	env_include ${includes[@]}

	local file_list=(	build.sh \
						dependencies.sh \
						get_dependencies.sh \
	)

	# arguments
	# input directory
	[ -z $1 ] && log_error "No directory specified" && exit || input_dir=$1
	# job - provided with the output {1}
	[ -z $2 ] && log_error "No job specified" && exit || job=$2

	# outputs
	# {1} - output of dir_job: $directory/$file
	source dir_job.sh

	dir_job $input_dir ${#file_list[@]} ${file_list[@]} $job ${@:3}
}

job()
{
	all_build_includes_dir_job $@
}
