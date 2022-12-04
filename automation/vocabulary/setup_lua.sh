#!/bin/bash
function job()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	local CUR_DIR=${PWD}

	cd "$THIS_DIR"
	source vocabulary_config.sh
	source ~/Scripts/automation/automation_config.sh
	
	source $scripts_dir/include/file_utils.sh
	source $scripts_dir/include/input.sh
	source $scripts_dir/include/log.sh

	log_prefix="[setup_lua] "
	
	local tmp_dir="tmp"
	[ ! -d "$tmp_dir" ] && mkdir "$tmp_dir"

	# download lua
	local lua="lua-5.4.4"
	local lua_download_url="http://www.lua.org/ftp/$lua.tar.gz"
	local download_path="$tmp_dir/lua.tar.gz"
	if [ -f "$download_path" ]; then
		log_info "Lua already downloaded"
	else
		log_info "Downloading Lua"
		curl -L "$lua_download_url" -o "$download_path"
	fi
	if [ -d "$tmp_dir/$lua" ]; then
		log_info "Lua already extracted"
	else
		log_info "Extracting Lua"
		tar -xzf "$download_path" -C "$tmp_dir"
	fi
	# cp "$tmp_dir/lua-5.4.4/src/lua.h" "$lua_dir/"
}

job $@