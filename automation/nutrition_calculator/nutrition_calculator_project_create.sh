#!/bin/bash
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CUR_DIR=${PWD}
proj_path="~/Projects/C++/nutrition_calculator"
source ~/Scripts/include/file_utils.sh

# remove the project folder if exists
rm -rf $proj_path

# create new project folder from template
../templates/cpp_cmake_project.sh nutrition_calculator ~/Projects/C++ exe

proj_automation_path="~/Scripts/automation/templates/nutrition_calculator"
cmake_file="$proj_path/CMakeLists.txt"

# add some special includes
file_replace $cmake_file "set\(SRC main.cpp \\$\{SRC\}\)" "set\(SRC main.cpp \$\{SRC\} \$\{INCLUDES_SRC\} \$\{UTILS_SRC\}\)"

# set the latest standard
addon_standard=$(<$proj_automation_path/CMakeLists_addon_standard.txt)
file_replace $cmake_file "set\(CMAKE_CXX_STANDARD 20\)" "$addon_standard"

# comment out some extra directories
file_insert_before "$cmake_file" "include_directories\(\".\"\)" "#"
file_insert_before "$cmake_file" "include_directories\(\\$\{PROJECT_BINARY_DIR\}\)" "#"

addon=$(<$proj_automation_path/CMakeLists_addon.txt)
#echo "addon: $addon"
#file_replace $proj_path/CMakeLists.txt "if \(NOT INCLUDES" "$addon"

cp -a ~/Projects/TMP/nutrition_calculator/. ~/Projects/C++/nutrition_calculator