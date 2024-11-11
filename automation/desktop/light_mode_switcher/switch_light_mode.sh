#!/bin/bash

function switch_light_mode()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../../automation_config.sh
	source $scripts_dir/include/log.sh
	source $scripts_dir/include/file_utils.sh
	
	local log_prefix="[set_light_mode]: "

	[ -z "$1" ] && log_error "No mode provided (use light or dark)" && return 1 || local mode=$(echo "${1,,}")

	log_info "Switching to '$mode' mode"

	if [ "$mode" == "dark" ]; then
		vscode_from="Light"
		vscode_to="Dark"
		win_theme="dark"
	elif [ "$mode" == "light" ]; then
		vscode_from="Dark"
		vscode_to="Light"
		win_theme="light"
	else
		log_error "Not supported mode '$mode'"
		return 2
	fi
	source $scripts_dir/include/file_utils.sh
	local home=$(powershell.exe $(to_win_path "$scripts_dir/automation/windows/envar.ps1") "USERPROFILE" | tr -d '\r\n')
	home=$(to_nix_path "$home")
	local full_path="$home/AppData/Roaming/Code/User/settings.json"
	file_replace "$full_path" "$vscode_from" "$vscode_to"
	[ $? -ne 0 ] && log_error "Failed to switch VSCode theme"
	powershell.exe "$(to_win_path $THIS_DIR/win_theme_switch.ps1)" "$win_theme"
	local plugins_dir="plugins"

	for file in $THIS_DIR/$plugins_dir/*; do
		source "$file" $@
	done

	return 0
}

switch_light_mode $@
[ $? -ne 0 ] && exit