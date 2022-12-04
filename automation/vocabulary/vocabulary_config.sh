#!/bin/bash
tmp=$THIS_DIR
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source $scripts_dir/include/os.sh
project_name=vocabulary
if is_mac; then
	project_parent_dir="${HOME}/Projects"
else
	project_parent_dir="${HOME}/Projects"
fi
project_dir=$project_parent_dir/$project_name
THIS_DIR=$tmp