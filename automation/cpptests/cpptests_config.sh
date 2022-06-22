#!/bin/bash
source ../automation_config.sh
source $scripts_dir/include/os.sh
if is_mac; then
	project_dir=${HOME}/Projects/CppTests
else
	project_dir=${HOME}/Projects/Tests/C++/CppTests
fi
