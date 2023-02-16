#!/bin/bash

function job()
{
    local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source $scripts_dir/include/log.sh
    local log_prefix="[vscode_cmaketools_settings_job]: "

    [ -z "$1" ] && log_error "No target path provided" && return 1 || local target_path="$1"

    [ ! -d "$target_path" ] && log_error "Not existent directory provided: '$target_path'" && return 10

    log_info "Add settings.json into '$target_path'"

    # include dependent scripts to the environment
    source automation_config.sh
    local includes=(	"$scripts_dir/include/file_utils.sh" \
                        "$scripts_dir/include/file_utils.py" \
                        "$scripts_dir/include/os.sh" \
    )
    env_include ${includes[@]}

    # do the job
    source $scripts_dir/automation/templates/templates_config.sh

    log "Setup project directory ..."

    cp -a $templates_dir/VSCode/CMakeTools/. $target_path
    [ $? -ne 0 ] && log_error "error while copying a module template" && return 4

    log_success "Template instantiated"
}

function vscode_cmaketools_settings_job()
{
    job $@
}
