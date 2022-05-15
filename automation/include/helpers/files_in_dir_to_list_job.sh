#!/bin/bash

# files_in_dir_to_list <dir_job> <input_dir> <files_list_dir_job> <final_job>

files_in_dir_to_list_job()
{
	local includes=(	"include" \
						"../include" \
	)
	env_include ${includes[@]}

	source log.sh
	local log_prefix="[files_in_dir_to_list_job]: "

	[ -z $1 ] && log "No dir job specified" && exit || dir_job_path=$1
	[ -z $2 ] && log "No input dir specified" && exit || input_dir=$2
	[ -z $3 ] && log "No files list dir job specified" && exit || files_list_dir_job_path=$3
	[ -z $4 ] && log "No final job specified" && exit || final_job_path=$4

	source $final_job_path

	local dir_job=$(basename $dir_job_path)
	local dir_job_name=$(echo $dir_job| cut -d. -f1)
	local files_list_dir_job=$(basename $files_list_dir_job_path)
	source $dir_job
	source $files_list_dir_job

	$dir_job_name swap_args_job.sh $input_dir inject_arg_job.sh $files_list_dir_job_path $final_job_path ${@:5}
}

job() 
{
	files_in_dir_to_list_job $@
}
