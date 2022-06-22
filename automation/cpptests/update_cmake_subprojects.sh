#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$THIS_DIR/../run.sh $THIS_DIR/all_subprojects_job.sh $THIS_DIR/update_cmake_subproject_job.sh
#$THIS_DIR/../run.sh $THIS_DIR/all_subprojects_job.sh $THIS_DIR/../automation/include/print_args_job.sh
