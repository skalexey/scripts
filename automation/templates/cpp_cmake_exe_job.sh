#!/bin/bash

function job()
{
    local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "$THIS_DIR/../automation_config.sh"
    source "$scripts_dir/include/log.sh"
    local log_prefix="[cpp_cmake_exe_job]: "

    [ -z $1 ] && log_error "No executable name provided" && return 1 || local exe_name=$1
    [ -z $2 ] && log_error "No target path provided" && return 2 || local target_path=$2

    log "Create CMake C++ executable '$exe_name' in '$target_path'"

    # set $exe_path
    local exe_path=$target_path/$exe_name

    if [ -d "$exe_path" ] || [ -f "$exe_path" ]; then
        log_error "This name is already taken"
        return 3
    fi

    #process args
    local includable=false
    local arg_index=0
    for arg in "$@" 
    do
        echo "arg[$arg_index]: '$arg'"
        
        if [[ $arg_index -gt 1 ]]; then
            log "Arg '$arg_index'"
            if [ "$arg" == "includable" ] || [ "$arg" == "-i" ]; then
                log "'$arg' option passed. Will create includable module .h and .cpp files"
                local includable=true
            fi
        else
            log "Skip arg '$arg_index'"
        fi	
        local arg_index=$((arg_index + 1))
    done

    # include dependent scripts to the environment
    source automation_config.sh
    local includes=(	"$scripts_dir/include/file_utils.sh" \
                        "$scripts_dir/include/file_utils.py" \
                        "$scripts_dir/include/os.sh" \
    )
    env_include ${includes[@]}

    # do the job
    source "$THIS_DIR/templates_config.sh"

    if $includable; then
        local template_name=ExeIncludable
    else
        local template_name=Exe
    fi

    log "Setup project directory ..."

    cp -R "$templates_dir/C++/$template_name" "$target_path"
    [ $? -ne 0 ] && log_error "error while copying a subproject template" && return 5
    cp -a "$templates_dir/CMake/C++/Exe/." "$target_path/$template_name"
    [ $? -ne 0 ] && log_error "error while copying a subproject template" && return 5
    local cmd="mv $target_path/Exe $exe_path"
    echo $cmd
    # return
    mv "$target_path/$template_name" "$exe_path"

    source "$scripts_dir/include/file_utils.sh"
    log_warning "Replace '$exe_path/CMakeLists.txt' with '$exe_name'"
    file_replace "$exe_path/CMakeLists.txt" "ExeTitle" "$exe_name"
    file_replace "$exe_path/main.cpp" "ExeTitle" "$exe_name"
    
    # rename includable module files
    if $includable; then
        mv "$exe_path/ExeTitle.h" "$exe_path/$exe_name.h"
        mv "$exe_path/ExeTitle.cpp" "$exe_path/$exe_name.cpp"
        file_replace "$exe_path/$exe_name.h" "ExeTitle" "$exe_name"
        file_replace "$exe_path/$exe_name.cpp" "ExeTitle" "$exe_name"
    fi

    if [ -f "$target_path/CMakeLists.txt" ]; then
        #file_insert_before $target_path/CMakeLists.txt "add_subdirectory" "add_subdirectory (\\\"$exe_name\\\")\n"
        file_append_line $target_path/CMakeLists.txt "add_subdirectory (\"$exe_name\")"
        returncode=$?
        [ $returncode -lt 0 ] && log_error "Error during executable directory registration in the root project: $returncode" && return 4
        log_success "Added subdirectory to the root project"
    fi
    [ $? -ne 0 ] && log_error "Error during executable directory creation: $?" && return 6

    log_success "Project directory created"
}

function cpp_cmake_exe_job()
{
    job $@
}
