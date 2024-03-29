#!/bin/bash

function job()
{
    local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source $scripts_dir/include/log.sh
    local log_prefix="[cpp_module_job]: "

    [ -z "$1" ] && log_error "No module name provided" && return 1 || local module_name="$1"
    [ -z "$2" ] && log_error "No target path provided" && return 2 || local target_path="$2"

    [ ! -d "$target_path" ] && log_error "Not existent directory provided: '$target_path'" && return 10

    log "Create C++ module '$module_name' in '$target_path'"

    # set $module_path
    local h_name="$target_path/$module_name.h"
    local cpp_name="$target_path/$module_name.cpp"

    if [ -f "$h_name" ] || [ -f "$cpp_name" ]; then
        log_error "This name is already taken"
        return 3
    fi

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

    cp -a $templates_dir/C++/Module/. $target_path
    [ $? -ne 0 ] && log_error "error while copying a module template" && return 4

    local cmd="mv $target_path/TplTitle.h $h_name"
    echo "$cmd"
    mv "$target_path/TplTitle.h" "$h_name"
    [ $? -ne 0 ] && log_error "error while moving a module template" && return 6

    local cmd="mv $target_path/TplTitle.cpp $cpp_name"
    echo $cmd
    mv "$target_path/TplTitle.cpp" "$cpp_name"
    [ $? -ne 0 ] && log_error "error while moving a module template" && return 7

    source $scripts_dir/include/file_utils.sh
    file_replace "$h_name" "{TPL_NAME}" "$module_name"
    file_replace "$cpp_name" "{TPL_NAME}" "$module_name"
    ec=$?
    [ $ec -ne 0 ] && log_error "Error during module temlate initialization: $c" && return 8

    log_success "Template instantiated"
}

function cpp_module_job()
{
    job $@
}
