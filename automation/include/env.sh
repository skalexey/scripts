#!/bin/bash

ENV_DIR=""

# This function copies all the given files and directories contents
# to the directory by the path from $ENV_DIR variable.
# If the variable $ENV_DIR is not set then nothing happens
env_include()
{
	[ -z "$ENV_DIR" ] && echo "[env_include()]: no environment is setup" && exit

	#arguments
	[ -z "$1" ] && exit || includes=$@ #includes

	# do the work
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/file_utils.sh
	source $scripts_dir/include/log.sh
	local log_prefix="\033[1;37m	[env_include()]: "
	local log_postfix="\033[0m"

	for e in ${includes[@]}; do
		if [[ $e == /* ]]; then
			local fp=$e
		else
			# includes are all relative to the target dir
			[ ! -z $ENV_TARGET_DIR ] && fp=$ENV_TARGET_DIR/$e || fp=$e
		fi
		[ -z "$fp" ] && log "empty path in includes: '$fp'" && continue
		# log "Process the include '$e' transformed into '$fp'"
		if [ -d "$fp" ]; then
			file0=$(ls -p $fp | grep -v / | head -1)
			# log $file0
			if [ ! -z file0 ]; then
				file0_name=$(basename $file0)
				[ -f $ENV_DIR/$file0_name ]	&& continue # log "Directory '$fp' is already included"
			fi
			log "Include directory '$fp'"
			cp $fp/* "$ENV_DIR/"
			continue
		fi
		if [ -f "$fp" ]; then
			fname=$(basename $fp)
			[ -f $ENV_DIR/$fname ] && continue # log "File '$fp' is already included"
			log "Include file '$fp'"
			cp $fp "$ENV_DIR/"
		else
			log "not a file or directory exists in the path '$fp'"
			continue
		fi
		#[ -d "$fp" ] && log "cp $fp/* \"$ENV_DIR/\"" || log "not a directory '$fp'"
		#[ -f "$fp" ] && log "cp $fp \"$ENV_DIR/\"" || log "not a file '$fp'"
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
	source $scripts_dir/include/log.sh
	local log_prefix="\033[1;37m	[setup_environment()]: "
	local log_postfix="\033[0m"

	# arguments 
	[ -z "$1" ] && exit || ENV_TARGET_DIR=$(dir_full_path "$1") # ENV_TARGET_DIR
	[ ! -z "$2" ] && local where_dir=$(dir_full_path "$2") || local where_dir="$ENV_TARGET_DIR" # where
	[ ! -z "$3" ] && local includes=${@:3} #includes

	# check the directories exists
	[ ! -d "$1" ] && log "No such directory passed in the first argument: '$1'" && exit

	# check the processed directories paths are not empty
	[ -z "$ENV_TARGET_DIR" ] && exit
	[ -z "$where_dir" ] && exit

	# do the work
	log "setup_environment in '$where_dir'"

	local target_name=$(basename $ENV_TARGET_DIR)
	local env_dir="$where_dir/env"

	# set the global ENV_DIR variable
	ENV_DIR=$env_dir

	log "ENV_DIR: $ENV_DIR"

	[ -d "$env_dir" ] && rm -rf $env_dir
	mkdir -p $env_dir
	# [ ! -d "$env_dir" ] && mkdir -p $env_dir

	# copy some essential dependencies
	cp "$THIS_DIR/../automation_config.sh" "$env_dir/"
	
	# copy include directories content to the env directory
	[ ! -z "$includes" ] && env_include ${includes[@]}

	# copy the target directory content into the env
	cp $ENV_TARGET_DIR/* "$env_dir/"
}
