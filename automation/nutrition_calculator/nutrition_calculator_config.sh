#!/bin/bash
tmp=$THIS_DIR
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source $scripts_dir/include/os.sh
if is_mac; then
	project_dir=${HOME}/Projects/nutrition_calculator
else
	project_dir=${HOME}/Projects/C++/nutrition_calculator
fi
THIS_DIR=$tmp