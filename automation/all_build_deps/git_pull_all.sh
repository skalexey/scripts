#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
$THIS_DIR/../run.sh $THIS_DIR/all_build_deps_job.sh $THIS_DIR/../include/helpers/git_pull_job.sh
