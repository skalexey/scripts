#!/bin/bash

# files_in_dir_to_list <dir_list_job> <input_dir> <files_list_dir_job> <final_job>

files_in_dir_to_list_job()
{
	source automation_config.sh
	local includes=(	"$scripts_dir/include" \
						"$automation_dir/include" \
	)
	env_include ${includes[@]}

	source log.sh
	local log_prefix="[files_in_dir_to_list_job]: "

	[ -z $1 ] && log_error "No dir job specified" && exit || dir_list_job_path=$1
	[ -z $2 ] && log_error "No input dir specified" && exit || input_dir=$2
	[ -z $3 ] && log_error "No files list dir job specified" && exit || files_list_dir_list_job_path=$3
	[ -z $4 ] && log_error "No final job specified" && exit || final_job_path=$4

	source $final_job_path

	local dir_job=$(basename $dir_list_job_path)
	local dir_list_job_name=$(echo $dir_job| cut -d. -f1)
	local files_list_dir_job=$(basename $files_list_dir_list_job_path)
	
	source $dir_job
	source $files_list_dir_job

	$dir_list_job_name swap_args_job.sh $input_dir inject_arg_job.sh $files_list_dir_list_job_path $final_job_path ${@:5}
}

job() 
{
	files_in_dir_to_list_job $@
}
