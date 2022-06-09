#!/bin/bash
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUR_DIR=${PWD}
proj_path="${HOME}/Projects/util_tools"
source ${HOME}/Scripts/include/file_utils.sh

# remove the project folder if exists
[ -d "$proj_path" ] && rm -rf $proj_path || echo "already removed"

# create new project folder from template
../templates/cpp_cmake_project.sh util_tools ~/Projects

../run.sh ../templates/cpp_cmake_exe_job.sh numbers_transform $proj_path

proj_automation_path="${HOME}/Scripts/automation/util_tools"
cmake_file="$proj_path/CMakeLists.txt"
	
# add some special includes
addon=$(<$proj_automation_path/CMakeLists_addon.txt)
file_replace $cmake_file "\{TPL_CUSTOM_INCLUDES\}" "$addon"
[ $? -ne 0 ] && echo "Error during adding the addon"
# copy main.cpp
cp $proj_automation_path/numbers_transform/main.cpp $proj_path/numbers_transform/main.cpp	

# set the latest standard
#addon_standard=$(<$proj_automation_path/CMakeLists_addon_standard.txt)
#file_replace $cmake_file "set\(CMAKE_CXX_STANDARD 20\)" "$addon_standard"

# comment out some extra directories
#file_insert_before "$cmake_file" "include_directories\(\".\"\)" "#"
#file_insert_before "$cmake_file" "include_directories\(\\$\{PROJECT_BINARY_DIR\}\)" "#"
