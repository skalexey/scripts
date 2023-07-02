#!/bin/bash

myrealpathnofollowsym () {
    for p in "$@"; do
        if ! printf '%s' "$p" | grep -q -- '^/'; then
            realpath -se "$PWD/$p"
        else
            realpath -se "$p"
        fi
    done
}

function box()
{
	local THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	cd "$THIS_DIR"
	local fpath="C:\Users\$USERNAME\Projects\tmp\python_test.txt"
	if [ -f "$fpath" ]; then
		rm "$fpath"
	fi
	source "automation_config.sh"
	source "$scripts_dir/include/log.sh"
	local log_prefix="[python_test]: "
	source $scripts_dir/include/file_utils.sh
	cp $scripts_dir/include/file_utils.py .
	
	local cur_path=${PWD}
	local win_cur_path=$(to_win_path "$cur_path")
	log_info "cur_path: '$cur_path', win_cur_path: '$win_cur_path'"
	local real_fpath=$(realpath --relative-to="$(to_win_path "${PWD}")" $fpath)

	# local real_path2=$(myrealpathnofollowsym "$fpath")
	log_info "Test file path: '$fpath', relative path: '$real_fpath', real_path2: '$real_path2'"
	echo "Test file contents" >> $fpath
	log_success "fpath: $fpath"
	local ret=$(python $THIS_DIR/file_utils.py replace "$fpath" "Test" "Awesome")
	# file_replace "$fpath" "Test" "Awesome"
	cat $fpath
}

box $@