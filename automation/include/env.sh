#!/bin/bash

# This function copies all the given files and directories contents
# to the directory by the path from $ENV_DIR variable.
# If the variable $ENV_DIR is not set then nothing happens
function env_include()
{
	[ -z "$ENV_DIR" ] && echo "[env_include()]: no environment is setup" && return 1

	#arguments
	[ -z "$1" ] && return 2 || includes=$@ #includes

	# do the work
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $ENV_DIR/automation_config.sh
	source $ENV_DIR/file_utils.sh
	source $ENV_DIR/log.sh
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

function setup_global_variables()
{
	local log_prefix="[setup_global_variables()]: "
	# log_info "setup_global_variables $1 $2"

	[ -z "$1" ] && log_error "No directory provided" && return 1 || ENV_TARGET_DIR=$(dir_full_path "$1") # ENV_TARGET_DIR - the invocable script directory
	[ ! -z "$2" ] && local where_dir=$(dir_full_path "$2") || local where_dir="$ENV_TARGET_DIR" # where we gonna create the environment

	[ -z "$where_dir" ] && log_error "where_dir has not been set" && return 2
	log_info "setup_environment in '$where_dir'"

	# set the global ENV_DIR variable
	ENV_DIR="$where_dir/env"

	log "ENV_DIR: $ENV_DIR"
	log "ENV_TARGET_DIR: $ENV_TARGET_DIR"
	# check the processed directories paths are not empty
	[ -z "$ENV_TARGET_DIR" ] && log_error "ENV_TARGET_DIR has not been set" && return 3
	[ -z "$ENV_DIR" ] && log_error "ENV_DIR has not been set" && return 3
	
	return 0
}

function include_essential()
{
	local log_prefix="\033[1;37m	[Auto include]: "
	local log_postfix="\033[0m"
	[ -z "$1" ] && log_error "No file provided" && return 1
	cp "$1" "$ENV_DIR/"
	[ $? -ne 0 ] && log_error "Error while including '$1'" || log "'$1'"
}

function setup_environment()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $scripts_dir/include/file_utils.sh
	source $scripts_dir/include/log.sh
	local log_prefix="[setup_environment()]: "

	# arguments 
	[ -z "$1" ] && log_error "No directory provided" && return 1
	# check the directories exists
	[ ! -d "$1" ] && log_error "Not existent directory passed in the first argument: '$1'" && return 2

	setup_global_variables $@
	[ $? -ne 0 ] && log_error "Error while calling setup_global_variables in '$1'" && return 3

	# do the work
	log_info "ENV_DIR: $ENV_DIR"

	[ -d "$ENV_DIR" ] && rm -rf $ENV_DIR
	mkdir -p $ENV_DIR
	# [ ! -d "$ENV_DIR" ] && mkdir -p $ENV_DIR

	[ ! -z "$3" ] && local includes=${@:3} #includes

	# include some essential dependencies
	include_essential "$automation_dir/automation_config.sh"
	include_essential "$scripts_dir/include/log.sh"
	include_essential "$scripts_dir/include/os.sh"
	include_essential "$scripts_dir/include/file_utils.sh"
	include_essential "$scripts_dir/include/file_utils.py"
	include_essential "$automation_dir/include/job.sh"
	include_essential "$automation_dir/run_local.sh"
	
	# copy include directories content to the env directory
	
	[ ! -z "$includes" ] && env_include ${includes[@]}

	# copy the target directory content into the env
	cp $ENV_TARGET_DIR/* "$ENV_DIR/"
}
