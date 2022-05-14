#!/bin/bash

ENV_DIR=""

# This function copies all the given files and directories contents
# to the directory by the path from $ENV_DIR variable.
# If the variable $ENV_DIR is not set then nothing happens
env_include()
{
	[ -z "$ENV_DIR" ] && echo "[env_include()]: no environment is setup" && exit

	#arguments
	[ -z "$1" ] && exit || includes=$1 #includes

	# do the work
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/file_utils.sh

	for e in ${includes[@]}; do
		[ -z "$e" ] && echo "[env_include()]: empty path in includes: '$e'" && continue

		fp=$scripts_dir/$e # full path
		
		[ -d "$fp" ] && cp $fp/* "$ENV_DIR/" && continue
		[ -f "$fp" ] && cp $fp "$ENV_DIR/" || echo "[env_include()]: not a file or directory exists in the path '$fp'"
		#[ -d "$fp" ] && echo "cp $fp/* \"$ENV_DIR/\"" || echo "not a directory '$fp'"
		#[ -f "$fp" ] && echo "cp $fp \"$ENV_DIR/\"" || echo "not a file '$fp'"
	done
}

# Creates environment directory called 'env' in the target directory passed as the
# first argument or in the specified directory by the second argument and copies
# every file from the target directory to 'env'.
# If the includes list is given as the third argument it then also call env_include
# for the given list
setup_environment()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/file_utils.sh

	# arguments 
	[ -z "$1" ] && exit || local target_dir=$(dir_full_path "$1") # target_dir
	[ ! -z "$2" ] && where_dir=$(dir_full_path "$2") || where_dir="$target_dir" # where
	[ ! -z "$3" ] && includes=$3 #includes

	# check the directories exists
	[ ! -d "$1" ] && echo "[setup_environment]: No such directory passed in the first argument: '$1'" && exit

	# check the processed directories paths are not empty
	[ -z "$target_dir" ] && exit
	[ -z "$where_dir" ] && exit

	# do the work
	echo "[setup_environment in '$where_dir']"

	local target_name=$(basename $target_dir)
	local env_dir="$where_dir/env"

	# set the global ENV_DIR variable
	ENV_DIR=$env_dir

	echo "[setup_environment]: ENV_DIR: $ENV_DIR"

	[ ! -d "$env_dir" ] && mkdir -p $env_dir

	# copy include directories content to the env directory
	[ ! -z "$includes" ] && env_include ${includes[@]}

	# copy the target directory content into the env
	cp $target_dir/* "$env_dir/"
}
