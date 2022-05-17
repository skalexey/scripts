#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $THIS_DIR/../automation_config.sh
source $scripts_dir/include/log.sh
log_prefix="[deliver_file.sh]: "

[ -z $1 ] && log_error "No file path provided" && exit

$automation_dir/run.sh \
    $THIS_DIR/all_build_deps_job.sh \
        $scripts_dir/include/swap_args_job.sh \
            $1 \
            $scripts_dir/include/copy_job.sh
