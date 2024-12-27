#!/bin/bash

# This job just executes the bash command line it receives as arguments replacing $1, $2, etc. with the arguments passed to this job
function custom_code_job()
{
	source log.sh
	local log_prefix="\033[0;33m[custom_code_job]\033[0m: "
	[ -z "$1" ] && exit
	local arg_count=0
	for arg in $@; do
		# Find the maximum argument index among arguments like "$1", "$2", etc.
		if [[ $arg =~ \$[0-9]+ ]]; then
			local arg_index=$(echo $arg | tr -d '$')
			[ $arg_index -gt $arg_count ] && arg_count=$arg_index
		fi
	done
	
	# Assemble the command line replacing $1, $2, etc. with the corresponding arguments from the beginning
	
	# Iterate all the arguments starting from $arg_count + 1 till the end of the all the arguments provided to this jobfor 
	# Should be as for i = arg_count + 1; i < $#; i++ do
	local cmd=""
	for ((i = arg_count+1; i <= $#; i++)); do
		# echo "${!i}"
		local arg="${!i}"
		if [[ $arg =~ \$[0-9]+ ]]; then
			# If the argument is a placeholder, replace it with the actual argument
			local arg_index=$(echo $arg | tr -d '$')
			cmd="$cmd \"${!arg_index}\""
		else
			# If the argument is not a placeholder, just append it to the command line
			cmd="$cmd $arg"
		fi
	done
	echo "Executing command: '$cmd'"
	eval "$cmd"

	[ -z "$1" ] && exit || log "\033[0;32m'$tmp'\033[0m"
}

job()
{
	custom_code_job $@
}
