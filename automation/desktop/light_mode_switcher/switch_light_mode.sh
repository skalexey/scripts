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
	local vscode_light_theme="Solarized Light"
	local vscode_dark_theme="Dark+"
	local python_bin=""

	if [ "$mode" == "dark" ]; then
		vscode_theme="$vscode_dark_theme"
		win_theme="dark"
	elif [ "$mode" == "light" ]; then
		vscode_theme="$vscode_light_theme"
		win_theme="light"
	else
		log_error "Not supported mode '$mode'"
		return 2
	fi
	if command -v python3 >/dev/null 2>&1; then
		python_bin="python3"
	elif command -v python >/dev/null 2>&1; then
		python_bin="python"
	else
		log_error "Python is required to switch VS Code theme"
		return 3
	fi

	"$python_bin" "$THIS_DIR/vscode_theme_switch.py" "$vscode_theme"
	[ $? -ne 0 ] && log_error "Failed to switch VSCode theme"

	if command -v powershell.exe >/dev/null 2>&1; then
		powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(to_win_path $THIS_DIR/win_theme_switch.ps1)" "$win_theme"
		powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(to_win_path $THIS_DIR/terminal_theme_switch.ps1)" "$win_theme"
	else
		log_info "powershell.exe not found; skipping Windows desktop/terminal theme switching"
	fi
	local plugins_dir="plugins"

	for file in $THIS_DIR/$plugins_dir/*; do
		source "$file" $@
	done

	return 0
}

switch_light_mode $@
[ $? -ne 0 ] && exit