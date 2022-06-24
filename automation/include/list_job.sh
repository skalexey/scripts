#!/bin/bash

# This job does other job on a given list of elements passed as an array

list_job()
{
	source log.sh
	local log_prefix="[list_job]: "

	# arguments 
	[ -z "$1" ] && log_error "Too few arguments. 0 of 3. Provide list size, list and job script" && exit # list_size
	[ -z "$2" ] && log_error "Too few arguments. 1 of 3. Provide list and job script" && exit # list
	[ -z "$3" ] && log_error "Too few arguments. 2 of 3. Provide job script" && exit # job
	# next all args for the job
	# next to the automatically passed list element as a first argument
	local list_size=$1
	#log "list_job: list_size: $list_size"
	local list=${@:2}
	local job_index=$((list_size+2))
	#log "list_job: job_index: $job_index"
	local job_path=${!job_index}
	local job=$(basename $job_path)
	source $job
	local jobname=$(echo $job| cut -d. -f1)
	#log "list_job: jobname: $jobname"
	#log "list_job: list: ${list[@]}"
	local counter=0
	for e in ${list[@]}; do
		#log "list_job: e: $e"
		local log_prefix="[list_job] [$counter/$list_size]: "
		cmd_args=("$e" "${@:$((job_index+1))}")
		local cmd="$jobname ${cmd_args[@]}"
		if $list_job_log; then
			log "command: $cmd"
		fi
		$jobname "$e" "${@:$((job_index+1))}"
		[ $counter -ge $((list_size-1)) ] && break || ((counter++))
	done
}

job()
{
	list_job $@
}