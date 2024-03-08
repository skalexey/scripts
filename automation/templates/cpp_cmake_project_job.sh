#!/bin/bash

function cpp_cmake_project_job()
{
    local THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source $scripts_dir/include/log.sh
    local log_prefix="[cpp_cmake_project_job.sh]: "

    [ -z $1 ] && log_error "No project name provided" && return 1 || local project_name="$1"
    [ -z $2 ] && log_error "No path provided" && return 2 || local parent_dir="$2"
    [ ! -z $3 ] && proj_type=$3

    log_info "Create project '$project_name' in '$parent_dir'"

    local includes=(	"$scripts_dir/include/file_utils.sh" \
                        "$scripts_dir/include/file_utils.py" \
                        "$scripts_dir/include/os.sh" \
    )
    env_include ${includes[@]}

    local project_path=$parent_dir/$project_name

    if [ -d "$project_path" ] || [ -f "$project_path" ]; then
        log_error "This name is already taken"
        exit 3
    fi

    #process args
    local arg_index=0
    local sub_mode=false
    for arg in "$@" 
    do
        log "arg[$arg_index]: '$arg'"
        if [[ $arg_index -gt 2 ]]; then
            if [ "$arg" == "sub" ]; then
                sub_mode=true
            fi
        fi	
        arg_index=$((arg_index + 1))
    done

    # do the job

    source $scripts_dir/automation/templates/templates_config.sh

    local project_tpl_dir=$templates_dir/CMake/C++/Project 

    log "Setup project directory ..."

    cp -R $project_tpl_dir $parent_dir

    mv $parent_dir/Project $project_path

    source $scripts_dir/include/file_utils.sh
    file_replace $project_path/CMakeLists.txt "Project" "$project_name"

    if [ "${proj_type^^}" == "LIB" ]; then
        rm $project_path/main.cpp
        rm -rf $project_path/Test
        file_replace $project_path/CMakeLists.txt "module_add_executable" "module_add_library"
    else
        log "'exe' option passed. Will create executable CMake project"
        rm -rf $project_path/Test
        file_replace $project_path/main.cpp "{PROJECT_NAME}" "$project_name"
    fi

    [ $? -ne 0 ] && log_error "Error during project directory creation: $?" && exit 4
    log_success "Project directory created"

    file_replace $project_path/CMakeLists.txt "{{PROJECT_NAME}}" "$project_name"

    log "Deliver build scripts ..."

    cp "$scripts_dir/automation/automation_config.sh" "$project_path"
    cp "$scripts_dir/include/log.sh" "$project_path"
    cp "$scripts_dir/include/os.sh" "$project_path"
    cp "$scripts_dir/include/file_utils.sh" "$project_path"
    cp "$templates_dir/Scripts/update_build_system.sh" "$project_path"
    cp "$templates_dir/Scripts/update_scripts.sh" "$project_path"
    cp "$templates_dir/Scripts/update_cmake_modules.sh" "$project_path"

    $project_path/update_build_system.sh
    retcode=$?
    [ $retcode -ne 0 ] && log_error "Error during build system delivery: $retcode" && exit 5

    log_success "Build scripts delivered"

    # $automation_dir/run.sh \
    #     $THIS_DIR/all_build_deps_job.sh \
    #         $scripts_dir/include/swap_args_job.sh \
    #             $1 \
    #             $scripts_dir/include/copy_job.sh
}
