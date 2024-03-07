#!/bin/bash

function pre_build()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"
	source log.sh
	local log_prefix="[pre_build]: "
	[ -z $1 ] && local dir_to_build="." || local dir_to_build=$1
	log_info "dir_to_build: '$dir_to_build'"
	
	# Choose whatever you need
	#./update_cmake_modules.sh $dir_to_build
	./update_cmake_modules.sh .
	#./update_cmake_modules.sh smth_else
}

pre_build $@