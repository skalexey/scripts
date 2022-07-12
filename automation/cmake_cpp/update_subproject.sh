#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source "$THIS_DIR/../../include/file_utils.sh"
$THIS_DIR/../run.sh $THIS_DIR/update_cmake_subproject_job.sh "$(full_path "$1")"
