#!/bin/bash

# files_in_dir_to_list 
#	<dir_list_job> 
#	<input_dir> 
#	<files_list_dir_job> 
#	<final_job>

files_in_dir_to_list_job()
{
    source automation_config.sh
	local includes=(	"$scripts_dir/include" \
						"$scripts_dir/automation/include" \
	)
	env_include ${includes[@]}

	source log.sh
	local log_prefix="[files_in_dir_to_list_job]: "

	[ -z $1 ] && log_error "No dir list job specified" && exit || dir_list_job_path=$1
	[ -z $2 ] && log_error "No input dir specified" && exit || input_dir=$2
	[ -z $3 ] && log_error "No files list dir job specified" && exit || files_list_dir_job_path=$3
	[ -z $4 ] && log_error "No final job specified" && exit || final_job_path=$4

	source $final_job_path

	local files_list_dir_job=$(basename $files_list_dir_job_path)
	local files_list_dir_job_name=$(echo $files_list_dir_job| cut -d. -f1)
	source $files_list_dir_job

	# call order explanation:
	# $files_list_dir_job_name \
	# $input_dir \
	# swap_args_job.sh \ # provided with the out {1} of $files_list_dir_job: $input_dir/$file
	# 	# <out {1} from $files_list_dir_job> = $input_dir/$file
	# 	swap_args_job.sh \ # called by $dir_list_job, provided with its out {1}
	# 	$dir_list_job_path \ # called by the first swap_args_job, provided with the second swap_args_job
	# 		# <out {1} from the first swap_args_job.sh> = swap_args_job.sh
	# 			# <out {2} from the first swap_args_job.sh> = out {1} from $files_list_dir_job = $input_dir/$file
	# 			# <out {1} from $files_list_dir_job> as a free argument = $input_dir/$file
	# 			$final_job_path \ # called by the second
	# 				# <out {1} from the second swap_args_job.sh>
	# 				# <out {2} from the second swap_args_job.sh>
	# 	${@:5}
	$files_list_dir_job_name \
		$input_dir \
		swap_args_job.sh \
			swap_args_job.sh \
			$dir_list_job_path \
					$final_job_path \
		${@:5}
}

job() 
{
	files_in_dir_to_list_job $@
}
