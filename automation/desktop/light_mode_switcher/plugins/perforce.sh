#!/usr/bin/bash

function switch_light_mode_perforce()
{
    local PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
    source $PARENT_DIR/../../automation_config.sh
    source $scripts_dir/include/log.sh
	local log_prefix="[switch_light_mode_perforce]: "
    [ -z "$1" ] && log_error "No mode provided (use light or dark)" && return 1 || local mode=$(echo "${1,,}")
    
    if [ "$mode" == "dark" ]; then
        value_from="false"
        value_to="true"
    elif [ "$mode" == "light" ]; then
        value_from="true"
        value_to="false"
    else
        log_error "Not supported mode '$mode'"
        return 2
    fi

    log_info "Switching light mode to '$mode'"
    
    source $scripts_dir/include/file_utils.sh
    home=$(powershell $scripts_dir/automation/windows/envar.ps1 "HOME")
    file_replace "$home\.p4qt\ApplicationSettings.xml" "\"DarkTheme\">$value_from" "\"DarkTheme\">$value_to"
    file_replace "$home\.p4merge\ApplicationSettings.xml" "\"DarkTheme\">$value_from" "\"DarkTheme\">$value_to"
}

switch_light_mode_perforce $@