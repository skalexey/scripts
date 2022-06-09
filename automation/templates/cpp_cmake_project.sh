#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source $scripts_dir/include/log.sh
log_prefix="[cpp_cmake_project.sh]: "

[ -z $1 ] && log_error "No project name provided" && exit 1 || project_name=$1
[ -z $2 ] && log_error "No target path provided" && exit 2 || target_path=$2
[ ! -z $3 ] && proj_type=$3

log "Create project '$project_name' in '$target_path'"

project_path=$target_path/$project_name

if [ -d "$project_path" ] || [ -f "$project_path" ]; then
    log_error "This name is already taken"
    exit 3
fi

#process args
arg_index=0
sub_mode=false
for arg in "$@" 
do
    echo "arg[$arg_index]: '$arg'"
    
    if [[ $arg_index -gt 2 ]]; then
        log "Arg '$arg_index'"
        if [ "$arg" == "sub" ]; then
            sub_mode=true
        fi
    else
        log "Skip arg '$arg_index'"
    fi	
    arg_index=$((arg_index + 1))
done

# do the job

source $THIS_DIR/templates_config.sh

project_tpl_dir=$templates_dir/CMake/Project 

log "Setup project directory ..."

cp -R $project_tpl_dir $target_path

mv $target_path/Project $project_path

source $scripts_dir/include/file_utils.sh
file_replace $project_path/CMakeLists.txt "Project" "$project_name"

if [ "${proj_type^^}" == "EXE" ]; then
    log "'exe' option passed. Will create executable CMake project"
    rm -rf $project_path/lib
    rm -rf $project_path/Test
    if ! $sub_mode ; then
        cp -a $project_path/exe/. $project_path
        rm -rf $project_path/exe/
        file_replace $project_path/CMakeLists.txt "Project" "$project_name"
    else
        log "'sub' option passed. Will create a subdirectory for the executable"
        rename $project_path/exe "$project_name"
        project_exe_dir=$project_path/$project_name
        file_replace $project_exe_dir/Project.cpp "Test" "$project_name"
        file_replace $project_exe_dir/Project.h "Test" "$project_name"
        rename $project_exe_dir/Test.cpp "$project_name.cpp"
        rename $project_exe_dir/Test.h "$project_name.h"
        file_replace $project_exe_dir/CMakeLists.txt "Test" "$project_name"
    fi
    file_replace $project_path/CMakeLists.txt "Test" "$project_name"
    
    [ $? -ne 0 ] && log_error "Error during project directory creation: $?" && exit 4
    log_success "Project directory created"
else
    rm -rf $project_path/exe
    rm -rf $project_path/lib
    rm -rf $project_path/Test
    file_replace $project_path/CMakeLists.txt "Project" "$project_name"
    #file_replace $project_path/CMakeLists.txt "{TPL_CUSTOM_INCLUDES}" ""
fi

log "Deliver build scripts ..."

cp -a "$scripts_dir/build_sh/." "$project_path"
cp "$scripts_dir/include/log.sh" "$project_path"
cp "$scripts_dir/include/os.sh" "$project_path"
cp "$scripts_dir/include/file_utils.sh" "$project_path"

[ $? -ne 0 ] && log_error "Error during build scripts delivery: $?" && exit 5
rename $project_path/build_config_example.sh build_config.sh
rename $project_path/deps_config_example.sh deps_config.sh
rename $project_path/deps_scenario_example.sh deps_scenario.sh
[ $? -ne 0 ] && log_error "Error during build scripts delivery: $?" && exit 5

log_success "Buld scripts delivered"

# $automation_dir/run.sh \
#     $THIS_DIR/all_build_deps_job.sh \
#         $scripts_dir/include/swap_args_job.sh \
#             $1 \
#             $scripts_dir/include/copy_job.sh
