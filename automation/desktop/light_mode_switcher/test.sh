#!/bin/bash

function switch_light_mode()
{
	local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	source $THIS_DIR/../automation_config.sh
	source $THIS_DIR/../../include/log.sh
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

	log "vscode_from: '$vscode_from'"
	log "vscode_to: '$vscode_to'"
	
	source $THIS_DIR/../../include/file_utils.sh
	
	file_replace "C:\Users\alexey.skorokhodov\AppData\Roaming\Code\User\settings.json" "$vscode_from" "$vscode_to"
	[ $? -ne 0 ] && log_error "Failed to switch VSCode theme" && return 3

	return 0
}

switch_light_mode $@
switch_light_mode_ret_code=$?
[ $switch_light_mode_ret_code -ne 0 ] && exit $switch_light_mode_ret_code