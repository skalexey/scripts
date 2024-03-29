#!/bin/bash

function run()
{
	# This script runs any job passed
	[ -z $1 ] && echo "[run script]: No job specified" && return 1 # job

	# include invironment helper
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/include/env.sh

	# store the current (invocation) dir for global usage
	local RUN_INVOCATION_DIR=${PWD}

	# collect all extra jobs passed as arguments to this script
	local arg_includes=()
	for arg in "$@" 
	do
		if [[ $arg =~ "_job.sh" ]]; then
			[[ $arg == /* ]] && local fp=$arg || local fp=$RUN_INVOCATION_DIR/$arg
			arg_includes+=($fp)
		fi
	done
	#echo "		arg_includes: ${arg_includes[@]}"

	# create env directory in the location of the passed job script
	# with copies of all scripts from the job script directory
	local TARGET_DIR=$(dirname $1)
	setup_environment $TARGET_DIR $TARGET_DIR ${arg_includes[@]}

	# go to the environment directory and call the same script from there
	cd $ENV_DIR

	source run_local.sh "$1" ${@:2}

	return $?
}

run $@
