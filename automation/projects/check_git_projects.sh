#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#$THIS_DIR/../run.sh $THIS_DIR/all_projects_job.sh $THIS_DIR/../include/print_args_job.sh
$THIS_DIR/../run.sh $THIS_DIR/all_projects_job.sh $THIS_DIR/../include/helpers/git_check_job.sh $THIS_DIR/../include/helpers/git_ask_and_commit_job.sh ${@:1}

