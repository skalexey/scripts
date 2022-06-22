#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/util_tools_config.sh
cmake_cpp_dir="$THIS_DIR/../cmake_cpp"
$THIS_DIR/../run.sh $cmake_cpp_dir/all_subprojects_job.sh $cmake_cpp_dir/update_cmake_subproject_job.sh "$project_dir"
#$THIS_DIR/../run.sh $cmake_cpp_dir/all_subprojects_job.sh $THIS_DIR/../automation/include/print_args_job.sh "$project_dir"
