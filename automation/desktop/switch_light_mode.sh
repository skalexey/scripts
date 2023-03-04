#!/bin/bash

function switch_light_mode()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $THIS_DIR/../../include/log.sh
	local log_prefix="[set_light_mode]: "

	[ -z "$1" ] && log_error "No mode provided (use light or dark)" && return || local mode=$(echo "${1,,}")

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

	source $THIS_DIR/../../include/file_utils.sh
	file_replace "C:\Users\skoro\AppData\Roaming\Code\User\settings.json" "$vscode_from" "$vscode_to" >> /dev/null
	[ $? -ne 0 ] && log_error "Failed to switch VSCode theme" && return 1
	powershell $THIS_DIR/win_theme_switch.ps1 "$win_theme"
	
	return 0
}

switch_light_mode $@
[ $? -ne 0 ] && exit