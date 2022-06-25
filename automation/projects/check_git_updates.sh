#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#$THIS_DIR/../run.sh $THIS_DIR/all_projects_job.sh $THIS_DIR/../include/print_args_job.sh
source $THIS_DIR/../automation_config.sh

filtered_fname="$automation_dir/projects/filtered_projects_to_update.txt"

if [ ! -f "$filtered_fname" ]; then
	$THIS_DIR/../run.sh $THIS_DIR/all_projects_job.sh $THIS_DIR/../../include/user_filter_job.sh "$filtered_fname"
fi

#$THIS_DIR/../run.sh $THIS_DIR/../include/file_list_job.sh "$THIS_DIR/filtered_projects_to_update.txt" $THIS_DIR/../include/print_args_job.sh
$THIS_DIR/../run.sh $THIS_DIR/../include/file_list_job.sh "$THIS_DIR/filtered_projects_to_update.txt" $THIS_DIR/../include/helpers/git_check_update_job.sh
