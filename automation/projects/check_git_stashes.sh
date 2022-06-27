#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh

filtered_fname="$automation_dir/projects/tmp/filtered_projects_to_check.txt"
echo "filtered_fname: $filtered_fname"
if [ ! -f "$filtered_fname" ]; then
	$THIS_DIR/../run.sh $THIS_DIR/all_projects_job.sh $THIS_DIR/../include/user_filter_job.sh "$filtered_fname"
fi

$THIS_DIR/../run.sh \
	$THIS_DIR/../include/file_list_job.sh \
		"$THIS_DIR/tmp/filtered_projects_to_check.txt" \
		$THIS_DIR/git_check_stash_job.sh
