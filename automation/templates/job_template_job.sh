#!/bin/bash

# job_template_job $name $target_path
# Creates a job with name $name at $target_path

function job_template_job()
{
	source automation_config.sh
	includes=(
		"$scripts_dir/include/os.sh" \
	)
	env_include ${includes[@]}
	source templates_config.sh
	source create_from_template_job.sh
	source log.sh
	local log_prefix="[job_template_job]: "
	[ -z "$1" ] && log_error "No job name provided" && return 1 || local job_name="$1"
	[ -z "$2" ] && log_error "No target path provided" && return 2 || local target_path="$2"
	create_from_template_job "$templates_dir/Scripts/job_template.sh" "${job_name}_job" "$target_path"
	return $?
}

function job()
{
	job_template_job $@
}
