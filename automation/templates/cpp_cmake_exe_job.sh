#!/bin/bash

function job()
{
    local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source $THIS_DIR/automation_config.sh
    source $scripts_dir/include/log.sh
    local log_prefix="[cpp_cmake_exe.sh]: "

    [ -z $1 ] && log_error "No executable name provided" && exit 1 || exe_name=$1
    [ -z $2 ] && log_error "No target path provided" && exit 2 || target_path=$2
    [ ! -z $3 ] && proj_type=$3

    log "Create CMake C++ executable '$exe_name' in '$target_path'"

    # set $exe_path
    local exe_path=$target_path/$exe_name

    if [ -d "$exe_path" ] || [ -f "$exe_path" ]; then
        log_error "This name is already taken"
        exit 3
    fi

    #process args
    local arg_index=0
    for arg in "$@" 
    do
        echo "arg[$arg_index]: '$arg'"
        
        if [[ $arg_index -gt 2 ]]; then
            log "Arg '$arg_index'"
            # chean an arg
        else
            log "Skip arg '$arg_index'"
        fi	
        local arg_index=$((arg_index + 1))
    done

    # include dependent scripts to the environment
    source automation_config.sh
    local includes=(	"$scripts_dir/include/file_utils.sh" \
                "$scripts_dir/include/file_utils.py" \
    )
    env_include ${includes[@]}

    # do the job
    source $THIS_DIR/templates_config.sh

    local project_tpl_dir=$templates_dir/CMake/Exe

    log "Setup project directory ..."

    cp -R $project_tpl_dir $target_path

    echo "mv $target_path/Exe $exe_path"
    # exit
    mv $target_path/Exe $exe_path

    source $scripts_dir/include/file_utils.sh
    file_replace $exe_path/CMakeLists.txt "ExeTitle" "$exe_name"
    file_replace $exe_path/main.cpp "ExeTitle" "$exe_name"
    if [ -f "$target_path/CMakeLists.txt" ]; then
        #file_insert_before $target_path/CMakeLists.txt "add_subdirectory" "add_subdirectory (\\\"$exe_name\\\")\n"
        file_append_line $target_path/CMakeLists.txt "add_subdirectory (\"$exe_name\")"
        exitcode=$?
        [ $exitcode -lt 0 ] && log_error "Error during executable directory registration in the root project: $exitcode" && exit 4
        log_success "Added subdirectory to the root project"
    fi
    [ $? -ne 0 ] && log_error "Error during executable directory creation: $?" && exit 5

    log_success "Project directory created"
}

function cpp_cmake_exe_job()
{
    job $@
}
