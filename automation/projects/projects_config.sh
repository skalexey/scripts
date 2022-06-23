#!/bin/bash

source automation_config.sh
source $scripts_dir/include/os.sh
source $scripts_dir/automation/templates/templates_config.sh
source $scripts_dir/automation/cpptests/cpptests_config.sh
cpptests_dir=$project_dir
project_list_stuff=( \
	"$scripts_dir" \
	"$templates_dir" \
	"$cpptests_dir" \
	"$projects_dir/C++/nutrition_calculator" \
)

# project_list_projects=( \
# 	"$projects_dir/Utils" \
# 	"$projects_dir/VL" \
# 	"$projects_dir/DataModelBuilder" \
# 	"$projects_dir/Networking" \
	
# )

