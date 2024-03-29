#!/bin/bash

job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	cd "$THIS_DIR"

	source android_config.sh
	
	local folderName=${PWD##*/}

	source "$root_dir/log.sh"
	local log_prefix="-- [${folderName} android init and build script]: "

	source android_init.sh
	source android_build.sh ${@:2}

	log_success "Finished everything" " -" " ---"
}

job $@